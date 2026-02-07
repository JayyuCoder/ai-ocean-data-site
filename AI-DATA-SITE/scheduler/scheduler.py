import logging
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from logging.handlers import TimedRotatingFileHandler

# Setup logging with rotation
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger('scheduler')
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(os.path.join(LOG_DIR, 'scheduler.log'), when='midnight', backupCount=7)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Prefer lightweight pipeline when TensorFlow/Postgres not available
try:
    from pipeline.run_pipeline import run_daily_pipeline as pipeline
    logger.info('Using full run_pipeline')
except Exception:
    try:
        from pipeline.run_pipeline_light import run_light_pipeline as pipeline
        logger.info('Using lightweight run_pipeline_light')
    except Exception:
        pipeline = None
        logger.warning('No pipeline available to schedule')

scheduler = BlockingScheduler(timezone=os.getenv("SCHED_TZ", "Asia/Kolkata"))

if pipeline is not None:
    def job_wrapper():
        logger.info('Scheduler triggered pipeline')
        try:
            pipeline()
            logger.info('Pipeline completed')
        except Exception as e:
            logger.exception('Pipeline failed: %s', e)

    scheduler.add_job(
        job_wrapper,
        trigger="cron",
        hour=int(os.getenv("SCHED_HOUR", "6")),
        minute=int(os.getenv("SCHED_MIN", "0")),
    )

if __name__ == "__main__":
    logger.info('Scheduler starting')
    scheduler.start()
