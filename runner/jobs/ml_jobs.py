from runner.config import Config
from runner.background_job import BackgroundJob
from apis.data_gen.xml_to_csv import voc_to_csv
from apis.data_gen.generate_tfrecord import gen_tfrecord
import uuid
import os
from apis.train_tf2.model_main_tf2 import train
from apis.train_tf2.exporter_main_v2 import export_model
from apis.inference.detect_objects import inference


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

    @app.task(bind=True)
    def train_model(self, path_to_saved_model, path_to_pipeline_config):
        task_id = self.request.id
        BackgroundJob.get_instance().set_status(task_id, "type", "ml")
        BackgroundJob.get_instance().set_status(
            task_id, "info", "Training")
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        # try:
        print(path_to_pipeline_config)
        train(path_to_saved_model, path_to_pipeline_config)
        BackgroundJob.get_instance().set_status(task_id, "status", "done")
        # except:
        #    BackgroundJob.get_instance().set_status(task_id, "status", "error")

    @app.task(bind=True)
    def export_model(self, path_to_checkpoint, path_to_pipeline_config, path_to_export):
        task_id = self.request.id
        BackgroundJob.get_instance().set_status(task_id, "type", "ml")
        BackgroundJob.get_instance().set_status(
            task_id, "info", "Exporting")
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        try:
            export_model(path_to_checkpoint,
                         path_to_pipeline_config, path_to_export)
            BackgroundJob.get_instance().set_status(task_id, "status", "done")
        except:
            BackgroundJob.get_instance().set_status(task_id, "status", "error")

    @app.task(bind=True)
    def inference_model(self, model_path, path_to_labelmap, images_dir, output_directory):
        task_id = self.request.id
        BackgroundJob.get_instance().set_status(task_id, "type", "ml")
        BackgroundJob.get_instance().set_status(
            task_id, "info", "Inferring")
        BackgroundJob.get_instance().set_status(task_id, "status", "start")
        # try:
        inference(model_path, path_to_labelmap,
                  images_dir, output_directory)
        BackgroundJob.get_instance().set_status(task_id, "status", "done")
        # except:
        #    BackgroundJob.get_instance().set_status(task_id, "status", "error")
