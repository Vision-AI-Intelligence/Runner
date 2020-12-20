from fastapi.params import Body
from runner.routers.DTOs.ml_dto import DatasetPath, PretrainedModel
from fastapi import APIRouter, Response, status
from runner.config import Config
from runner.job import mlJob, ioJob
import os

router = APIRouter()
config = Config.get_instance().get_config()


@router.get("/models/{pid}")
def get_models(pid: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    models = []
    for dir in os.listdir(os.path.join(project_loc, 'models')):
        if os.path.isdir(dir):
            models.append(dir)
    return {"models": models}


@router.post("/gen_tfrecord/{pid}")
def gen_tfrecord(pid: str, response: Response, data_path: DatasetPath = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    data_path.path_to_annotation = os.path.join(
        project_loc, 'data', data_path.path_to_annotation)
    data_path.path_to_images = os.path.join(
        project_loc, 'data', data_path.path_to_images)
    data_path.path_to_label_map = os.path.join(
        project_loc, 'data', data_path.path_to_label_map)
    data_path.path_to_tfrecord = os.path.join(
        project_loc, 'data', data_path.path_to_tfrecord)
    job = mlJob.gen_tfrecord.delay(pid,
                                   data_path.path_to_images, data_path.path_to_annotation, data_path.path_to_label_map, data_path.path_to_tfrecord)
    return {"jobId": job.id}


@router.post("/download_pretrained_model/{pid}")
def download_pretrained_model(pid: str, response: Response, pretrained_model: PretrainedModel = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}

    job = ioJob.download.delay(pretrained_model.url, os.path.join(
        project_loc, 'models', pretrained_model.name), True)
    return {"jobId": job.id}
