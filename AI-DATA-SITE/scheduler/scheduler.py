from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline.run_pipeline import run_daily_pipeline

scheduler = BlockingScheduler(timezone="Asia/Kolkata")

scheduler.add_job(
    run_daily_pipeline,
    trigger="cron",
    hour=6,
    minute=0
)

scheduler.start()
