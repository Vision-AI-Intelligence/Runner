from runner.background_job import BackgroundJob
import requests
import zipfile
import tarfile
import os
import shutil


class IOJob(BackgroundJob):

    app = BackgroundJob.get_instance().celery_app

    @app.task(bind=True)
    def unzip(self, filename):
        print("Unzipping...")
        task_id = self.request.id
        BackgroundJob.get_instance().set_status(task_id, "type", "io")
        BackgroundJob.get_instance().set_status(task_id, "info", "Unzip: "+filename)
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        try:
            if filename.endwiths(".zip"):
                with zipfile.ZipFile(filename) as zip_ref:
                    zip_ref.extractall(os.path.dirname(filename))
            else:
                with tarfile.TarFile(filename) as tar_ref:
                    tar_ref.extractall(os.path.dirname(filename))
        except:
            BackgroundJob.get_instance().set_status(task_id, "status", "error")
            return
        BackgroundJob.get_instance().set_status(task_id, "status", "done")

    @app.task(bind=True)
    def zip(self, dir: str):
        task_id = self.request.id
        BackgroundJob.get_instance().set_status(task_id, "type", "io")
        BackgroundJob.get_instance().set_status(task_id, "info", "Zip "+dir)
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        filename = os.path.basename(dir)
        try:
            with zipfile.ZipFile(os.path.join(os.path.dirname(dir), filename+".zip"), "w", zipfile.ZIP_DEFLATED) as zip_ref:
                for root, dirs, files in os.walk(dir):
                    print(root)
                    for file in files:
                        zip_ref.write(os.path.join(root, file))
        except:
            BackgroundJob.get_instance().set_status(task_id, "status", "error")
            return
        BackgroundJob.get_instance().set_status(task_id, "status", "done")

    @app.task(bind=True)
    def download(self, url, filename, unzip=False):
        print("Downloading...")
        task_id = self.request.id
        print(task_id)
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        BackgroundJob.get_instance().set_status(task_id, "type", "io")
        BackgroundJob.get_instance().set_status(task_id, "info", "Download: "+url)
        try:
            res = requests.get(url=url, stream=True)
            total_size = int(res.headers.get("content-length", 0))
            downloaded_size = 0

            BackgroundJob.get_instance().set_status(task_id, "total_size", total_size)
            BackgroundJob.get_instance().set_status(
                task_id, "downloaded_size", 0)
            block_size = 1024
            report_quotas = 1024
            report_progress = 0
            with open(filename, 'wb') as file:
                for data in res.iter_content(block_size):
                    file.write(data)
                    downloaded_size += len(data)
                    report_progress += 1
                    if report_progress == report_quotas:
                        BackgroundJob.get_instance().set_status(
                            task_id, "downloaded_size", downloaded_size)
                        report_progress = 0
            BackgroundJob.get_instance().set_status(
                task_id, "downloaded_size", total_size)
            BackgroundJob.get_instance().set_status(task_id, "status", "done")
        except:
            BackgroundJob.get_instance().set_status(task_id, "status", "error")
            return
        if unzip:
            BackgroundJob.get_instance().set_status(task_id, "status", "unzipping")
            try:
                if filename.endwiths(".zip"):
                    with zipfile.ZipFile(filename) as zip_ref:
                        zip_ref.extractall(os.path.dirname(filename))
                else:
                    with tarfile.TarFile(filename) as tar_ref:
                        tar_ref.extractall(os.path.dirname(filename))
                BackgroundJob.get_instance().set_status(task_id, "status", "done")
            except:
                BackgroundJob.get_instance().set_status(task_id, "status", "error")
