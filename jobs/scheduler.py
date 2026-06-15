from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from database.connection import SessionLocal, init_db
from jobs.daily_radar_job import DailyRadarJob

logger = logging.getLogger(__name__)

SCHEDULER_TIMEZONE = "America/Sao_Paulo"


def run_daily_radar() -> None:
    db = SessionLocal()
    try:
        job = DailyRadarJob(db)
        message = job.run()
        logger.info("Radar diário enviado com sucesso.")
        if settings.debug:
            logger.debug(message.replace("<b>", "").replace("</b>", ""))
    except Exception:
        logger.exception("Erro ao executar radar diário")
    finally:
        db.close()


def create_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone=SCHEDULER_TIMEZONE)
    scheduler.add_job(
        run_daily_radar,
        CronTrigger(
            hour=settings.radar_schedule_hour,
            minute=settings.radar_schedule_minute,
            timezone=SCHEDULER_TIMEZONE,
        ),
        id="daily_radar",
        replace_existing=True,
        max_instances=1,
    )
    return scheduler


def start_scheduler() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    init_db()
    scheduler = create_scheduler()

    hour = settings.radar_schedule_hour
    minute = settings.radar_schedule_minute
    logger.info(
        "Scheduler iniciado. Radar diário agendado para %02d:%02d (%s).",
        hour,
        minute,
        SCHEDULER_TIMEZONE,
    )
    logger.info("Pressione Ctrl+C para encerrar.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler encerrado.")
