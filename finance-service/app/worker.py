import json
import logging
import os
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

import pika
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker, StreamLostError
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Invoice
from app.schemas import UsageRecordedEvent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("billing-worker")

EXCHANGE_NAME = "siudes.events"
EXCHANGE_TYPE = "topic"
QUEUE_NAME = "finance.billing.queue"
ROUTING_KEY = "usage.recorded"
TWO_PLACES = Decimal("0.01")

running = True
active_connection: pika.BlockingConnection | None = None
active_channel: pika.adapters.blocking_connection.BlockingChannel | None = None


def handle_signal(signum, frame):
    global running
    logger.info("Received signal %s, shutting down...", signum)
    running = False
    if active_connection and active_connection.is_open and active_channel and active_channel.is_open:
        try:
            active_connection.add_callback_threadsafe(active_channel.stop_consuming)
        except Exception:
            pass


signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def _build_sync_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    user = os.getenv("POSTGRES_USER", "siudes")
    password = os.getenv("POSTGRES_PASSWORD", "siudes123")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("FINANCE_DB_NAME", "db_siudes_finance")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


engine = create_engine(_build_sync_database_url(), echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db_sync(max_retries: int = 10, retry_delay: int = 2) -> None:
    """Ensure database tables exist before consuming messages."""
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database connection verified and tables ready.")
            return
        except (OperationalError, InterfaceError) as exc:
            if not running or attempt == max_retries:
                raise
            logger.warning(
                "Database not ready (attempt %d/%d): %s. Retrying in %ds...",
                attempt,
                max_retries,
                exc,
                retry_delay,
            )
            time.sleep(retry_delay)


def _generate_invoice_code() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    uid_part = uuid.uuid4().hex[:8].upper()
    return f"INV-{date_part}-{uid_part}"


def _process_message(ch, method, properties, body: bytes) -> None:
    delivery_tag = method.delivery_tag

    try:
        raw_payload = json.loads(body.decode("utf-8"), parse_float=Decimal)
        event = UsageRecordedEvent.model_validate(raw_payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
        logger.warning("Invalid message payload (delivery_tag=%s): %s", delivery_tag, exc)
        ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
        return

    usage_amount = event.usage_amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    tariff_rate = event.tariff_rate.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    total_amount = (event.usage_amount * event.tariff_rate).quantize(
        TWO_PLACES, rounding=ROUND_HALF_UP
    )
    invoice_code = _generate_invoice_code()

    session = SessionLocal()
    try:
        stmt = (
            pg_insert(Invoice)
            .values(
                invoice_code=invoice_code,
                event_id=event.event_id,
                customer_code=event.customer_code,
                unit_type=event.unit_type,
                usage_amount=usage_amount,
                tariff_rate=tariff_rate,
                total_amount=total_amount,
                status="UNPAID",
                issued_at=event.recorded_at,
            )
            .on_conflict_do_nothing(index_elements=["event_id"])
        )
        result = session.execute(stmt)
        session.commit()

        if result.rowcount and result.rowcount > 0:
            logger.info(
                "Created invoice %s for event_id=%s (customer=%s, unit=%s, total=%s)",
                invoice_code,
                event.event_id,
                event.customer_code,
                event.unit_type,
                total_amount,
            )
        else:
            logger.info(
                "Duplicate event_id=%s ignored idempotently; acknowledging message.",
                event.event_id,
            )

        ch.basic_ack(delivery_tag=delivery_tag)
    except (OperationalError, InterfaceError) as exc:
        session.rollback()
        logger.error(
            "Transient database error for event_id=%s: %s. Requeueing after short delay...",
            event.event_id,
            exc,
        )
        time.sleep(2)
        ch.basic_nack(delivery_tag=delivery_tag, requeue=True)
    except Exception:
        session.rollback()
        logger.exception("Unexpected error processing event_id=%s", event.event_id)
        ch.basic_nack(delivery_tag=delivery_tag, requeue=False)
    finally:
        session.close()


def _create_rabbitmq_connection() -> pika.BlockingConnection:
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "siudes")
    password = os.getenv("RABBITMQ_PASS", "siudes123")

    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
    )
    return pika.BlockingConnection(parameters)


def main() -> None:
    global active_connection, active_channel

    logger.info("Starting SIUDES billing-worker...")
    init_db_sync()

    retry_delay = 3
    while running:
        try:
            active_connection = _create_rabbitmq_connection()
            active_channel = active_connection.channel()

            active_channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type=EXCHANGE_TYPE,
                durable=True,
            )
            active_channel.queue_declare(queue=QUEUE_NAME, durable=True)
            active_channel.queue_bind(
                queue=QUEUE_NAME,
                exchange=EXCHANGE_NAME,
                routing_key=ROUTING_KEY,
            )
            active_channel.basic_qos(prefetch_count=1)
            active_channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=_process_message,
                auto_ack=False,
            )

            logger.info(
                "Connected to RabbitMQ. Listening on queue '%s' (exchange='%s', routing_key='%s')",
                QUEUE_NAME,
                EXCHANGE_NAME,
                ROUTING_KEY,
            )
            active_channel.start_consuming()
        except (AMQPConnectionError, StreamLostError, ChannelClosedByBroker, OSError) as exc:
            if not running:
                break
            logger.warning(
                "RabbitMQ connection error: %s. Retrying in %ds...",
                exc,
                retry_delay,
            )
            time.sleep(retry_delay)
        finally:
            if active_connection and active_connection.is_open:
                try:
                    active_connection.close()
                except Exception:
                    pass
            active_channel = None
            active_connection = None

    logger.info("SIUDES billing-worker stopped.")
    sys.exit(0)


if __name__ == "__main__":
    main()
