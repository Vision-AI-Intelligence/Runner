from runner.routers.DTOs.io_dto import DeletedFile, DownloadedFile, UnzippedFile
from fastapi import APIRouter, UploadFile, File, status, Response, Body
from runner.config import Config
import os
import shutil
from runner.job import ioJob

router = APIRouter()
config = Config.get_instance().get_config()


@router.get("/")
def ping():
    return {"message": "Hello World"}


@router.get("/project")
def listing():
    projectIds = os.listdir(config['storage'])
    return {"projects": projectIds}


@router.get("/project/{pid}/walk")
def file_walk(pid: str, dir: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    files = []
    folders = []
    project_loc = os.path.join(project_loc, dir)
    for file in os.listdir(project_loc):
        if os.path.isfile(os.path.join(project_loc, file)):
            files.append(file)
        else:
            folders.append(file)
    return {
        "files": files,
        "folders": folders
    }


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


@router.post("/project/{pid}/data")
def upload_data(pid: str, response: Response, upload_file: UploadFile = File(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    try:
        with open(os.path.join(project_loc, 'data', upload_file.filename), "wb+") as des_file:
            shutil.copyfileobj(upload_file.file, des_file)
        return {"message": "Uploaded"}
    except:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Cannot upload file [{}]".format(upload_file.filename)}


@router.post("/project/{pid}/download")
def download_data(pid: str, response: Response, file: DownloadedFile = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    job = ioJob.download.delay(file.url, os.path.join(
        project_loc, file.section, file.filename))
    return {"jobId": job.id}


@router.post("/project/{pid}/zip")
def unzip_file(pid: str, response: Response, file: UnzippedFile = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    job = ioJob.zip.delay(os.path.join(project_loc, 'data', file.filename))
    return {"jobId": job.id}


@router.post("/project/{pid}/unzip")
def unzip_file(pid: str, response: Response, file: UnzippedFile = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    job = ioJob.unzip.delay(os.path.join(project_loc, 'data', file.filename))
    return {"jobId": job.id}


@router.delete("/project/{pid}/rm")
def delete_file(pid: str, response: Response, file: DeletedFile = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    shutil.rmtree(os.path.join(project_loc, 'data',
                               file.filename), ignore_errors=True)
    return {"message": "Delete [{}]".format(file.filename)}
