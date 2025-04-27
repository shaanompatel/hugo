from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

# module‐level variable to track whether we've already started
_scheduler = None

def fetch_mail_job():
    try:
        call_command("getmail", verbosity=0)
        logger.info("getmail ran successfully")
    except Exception:
        logger.exception("Error running getmail")

def start():
    global _scheduler
    if _scheduler:
        # already started; do nothing
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        fetch_mail_job,
        trigger="interval",
        minutes=0.25,
        id="fetch-mail-job",
        replace_existing=True,
    )
    _scheduler.start()

    logger.info("APS scheduler started")