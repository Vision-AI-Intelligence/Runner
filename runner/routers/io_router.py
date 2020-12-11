from fastapi import APIRouter, UploadFile, status
from starlette.responses import Response
from runner.config import Config
import os
import shutil

router = APIRouter()
config = Config.get_instance().get_config()


@router.get("/")
def ping():
    return {"message": "Hello World"}


@router.post("/project/{pid}")
def create_project(pid: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] already existed".format(pid)}
    os.mkdir(project_loc)
    os.mkdir(os.path.join(project_loc, "data"))
    os.mkdir(os.path.join(project_loc, "models"))
    os.mkdir(os.path.join(project_loc, "downloaded"))
    response.status_code = status.HTTP_201_CREATED
    return {"message": "Project [{}] was created".format(pid)}


@router.delete("/project/{pid}")
def delete_project(pid: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    shutil.rmtree(project_loc)
    response.status_code = status.HTTP_200_OK
    return {"message": "Project [{}] was deleted".format(pid)}
