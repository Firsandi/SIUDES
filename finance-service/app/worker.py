import logging
import signal
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("billing-worker")

running = True


def handle_signal(signum, frame):
    global running
    logger.info("Received signal %s, shutting down...", signum)
    running = False


signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def main():
    logger.info("SIUDES billing-worker skeleton started and waiting for tasks...")
    while running:
        time.sleep(5)
    logger.info("SIUDES billing-worker stopped.")
    sys.exit(0)


if __name__ == "__main__":
    main()
