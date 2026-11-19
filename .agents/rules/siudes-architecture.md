# SIUDES - Architecture & V-Del Guidelines

## 1. Tech Stack & Monorepo Structure
- SDLC: V-Model (Strict Verification & Validation; NO Agile/Sprint refactoring).
- /unit-service: Laravel 13 (PHP 8.3+), PostgreSQL (db_siudes_unit), RabbitMQ Publisher (php-amqplib).
- /finance-service: Python 3.12+ FastAPI, SQLAlchemy/AsyncPG, PostgreSQL (db_siudes_finance), Pika RabbitMQ Consumer, SSE (sse-starlette).
- /frontend: Vue 3 (Composition API script setup), Vite, Tailwind CSS.
- /nginx: Reverse proxy routing /api/unit/* -> Laravel, /api/finance/* -> FastAPI, /* -> Vue 3.

## 2. Distributed System Contracts (STRICT - DO NOT ALTER)
- Database Isolation: unit-service ONLY accesses db_siudes_unit. finance-service ONLY accesses db_siudes_finance. Cross-service communication MUST use RabbitMQ or REST API.
- RabbitMQ Topology:
  - Exchange: siudes.events (type: topic, durable: true)
  - Routing Key: usage.recorded
  - Queue: finance.billing.queue (durable: true)
  - Publisher: persistent messages (delivery_mode=2) + publisher confirms.
  - Consumer: MUST set prefetch_count=1 and manual_ack ONLY after PostgreSQL transaction commits. Invalid payload => nack(requeue=False); transient error => requeue with max retries.
- Standard Event Payload (usage.recorded):
  {"event_id": "uuid-v4", "unit_type": "AIR | SAMPAH | ALSINTAN", "customer_code": "PLG-001", "usage_amount": 15.5, "tariff_rate": 2500, "recorded_at": "2026-11-19T12:00:00Z"}
- Idempotency & Concurrency:
  - invoices.event_id MUST be UNIQUE; insert using ON CONFLICT DO NOTHING (duplicate => ack, no error).
  - Cashier payment endpoint MUST use PostgreSQL Pessimistic Locking (SELECT ... FOR UPDATE). Paying an already PAID invoice MUST return HTTP 409.

## 3. Conventions & Role Matrix
- Response JSON: {"success": bool, "data": any, "error": {"code": str, "message": str} | null}
- Status codes: 401 (no X-User-Role header), 403 (wrong role), 404, 409 (duplicate payment), 422 (validation).
- Money: NUMERIC(14,2) / Decimal only. NEVER float. total = usage_amount * tariff_rate. All timestamps UTC ISO-8601.
- Nginx: SSE route (/api/finance/stream) MUST set proxy_buffering off and long proxy_read_timeout.
- Roles (enforced in backend): ADMIN_UNIT (POST usage, CRUD master), KASIR (list & pay invoices), KEPALA_DESA (read-only dashboard).

## 4. Agent Behavior
- Work ONLY within the ticket scope. Never touch other services or the other DB.
- Write a plan first and STOP for approval before editing files.
- Never alter Section 2 contracts; if a contract seems wrong, stop and report.
- No new dependencies without asking.
- Done = builds, /health OK, verification output shown, and notes appended to docs/devlog.md.
- Secrets only via .env; commit .env.example. Use make targets.
