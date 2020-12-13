from fastapi.params import Body
from runner.routers.DTOs.ml_dto import DatasetPath
from fastapi import APIRouter, Response, status
from runner.config import Config
from runner.job import mlJob
import os

router = APIRouter()
config = Config.get_instance().get_config()


@router.post("/gen_tfrecord/{pid}")
def gen_tfrecord(pid: str, response: Response, data_path: DatasetPath = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] already existed".format(pid)}
    data_path.path_to_annotation = os.path.join(
        project_loc, 'data', data_path.path_to_annotation)
    data_path.path_to_images = os.path.join(
        project_loc, 'data', data_path.path_to_images)
    data_path.path_to_label_map = os.path.join(
        project_loc, 'data', data_path.path_to_label_map)
    job = mlJob.gen_tfrecord.delay(
        data_path.path_to_images, data_path.path_to_annotation, data_path.path_to_label_map, data_path.path_to_tfrecord)
    return {"jobId": job.id}
