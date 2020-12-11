from runner.background_job import BackgroundJob
from runner.jobs.io_jobs import IOJob
from runner.jobs.ml_jobs import MLJob

app = BackgroundJob.get_instance().celery_app

ioJob = IOJob()
mlJob = MLJob()
