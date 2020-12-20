from runner.config import Config
from runner.background_job import BackgroundJob
from apis.data_gen.xml_to_csv import voc_to_csv
from apis.data_gen.generate_tfrecord import gen_tfrecord
import uuid
import os


class MLJob(BackgroundJob):

    app = BackgroundJob.get_instance().celery_app

    @app.task(bind=True)
    def gen_tfrecord(self, pid, path_to_images, path_to_annot, path_to_label_map, path_to_save_tfrecords):
        task_id = self.request.id
        config = Config.get_instance().get_config()
        BackgroundJob.get_instance().set_status(task_id, "type", "ml")
        BackgroundJob.get_instance().set_status(
            task_id, "info", "Generate TF: "+path_to_save_tfrecords)
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        # try:
        file_csv_name = str(uuid.uuid1())+".csv"
        file_csv_path = os.path.join(config['storage'], pid, file_csv_name)
        voc_to_csv(path_to_annot, file_csv_path)
        gen_tfrecord(path_to_images, file_csv_path,
                     path_to_label_map, path_to_save_tfrecords)
        # except:
        #    BackgroundJob.get_instance().set_status(task_id, "status", "error")
        #    return
        BackgroundJob.get_instance().set_status(task_id, "status", "done")
