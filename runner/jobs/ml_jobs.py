from runner.background_job import BackgroundJob


class MLJob(BackgroundJob):

    app = BackgroundJob.get_instance().celery_app

    @app.task()
    def unzip(filename):
        print("Unzipping...")

    @app.task()
    def download(url, filename, dir):
        print("Downloading...")

    @app.task()
    def add(a, b):
        return a+b
