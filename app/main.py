import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import FETCH_INTERVAL_MINUTES
from app.database import init_db
from app.fetcher import fetch_and_save

MSK = timezone(timedelta(hours=3))


def log_next_run():
    logger = logging.getLogger(__name__)
    now = datetime.now(timezone.utc)
    next_run = now + timedelta(minutes=FETCH_INTERVAL_MINUTES)
    logger.info(
        "Next run at %s UTC / %s MSK",
        next_run.strftime("%H:%M:%S"),
        next_run.astimezone(MSK).strftime("%H:%M:%S"),
    )


def setup_logging():
    Path("logs").mkdir(exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # все события
    info_handler = logging.handlers.RotatingFileHandler("logs/app.log",
                                                        maxBytes=5_000_000,
                                                        backupCount=3)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(fmt)

    # лог ошибок
    error_handler = logging.handlers.RotatingFileHandler("logs/errors.log",
                                                         maxBytes=5_000_000,
                                                         backupCount=3)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[info_handler, error_handler, console_handler])


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting currency tracker")
    init_db()

    fetch_and_save()
    log_next_run()

    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_and_save,
                      trigger="interval",
                      minutes=FETCH_INTERVAL_MINUTES,
                      id="fetch_rates")
    scheduler.add_job(log_next_run,
                      trigger="interval",
                      minutes=FETCH_INTERVAL_MINUTES,
                      id="log_next_run")

    logger.info("Scheduler started, interval: %d min", FETCH_INTERVAL_MINUTES)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
