from fastapi.params import Body
from runner.routers.DTOs.ml_dto import ConfigPipelineRequestModel, DatasetPath, InferenceRequestModel, PretrainedModel, TrainParams
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
        if os.path.isdir(os.path.join(project_loc, 'models', dir)):
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
    print(pretrained_model)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}

    job = ioJob.download_model.delay(pretrained_model.url, os.path.join(
        project_loc, 'models', pretrained_model.name), True)
    return {"jobId": job.id}


@router.get("/train/{pid}/{model}")
def get_trains(pid: str, model: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    if not os.path.exists(os.path.join(project_loc, 'models', model)):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Model [{}] not found".format(model)}
    res = {}
    try:
        res = {"trains": os.listdir(os.path.join(
            project_loc, 'models', model, 'customs'))}
    except:
        res = {"trains": []}
    return res


@router.post("/train/{pid}/{model}/{train}")
def create_train(pid: str, model: str, train: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    if not os.path.exists(os.path.join(project_loc, 'models', model)):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Model [{}] not found".format(model)}
    os.makedirs(os.path.join(project_loc, 'models', model, 'customs', train))
    res = {}
    try:
        res = {"trains": os.listdir(os.path.join(
            project_loc, 'models', model, 'customs'))}
    except:
        res = {"trains": []}
    return res


@router.get("/pipeline/{pid}/{model}")
def get_pipeline(pid: str, model: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    if not os.path.exists(os.path.join(project_loc, 'models', model)):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Model [{}] not found".format(model)}
    try:
        config_str = ""
        with open(os.path.join(project_loc, 'models', model, 'pipeline.config'), 'r') as pipeline_conf:
            config_str = pipeline_conf.read()
        return {'config': config_str}
    except:
        return {'message': 'Cannot read config'}


@router.post("/pipeline/{pid}/{model}/{train}")
def edit_pipeline(pid: str, model: str, train: str, response: Response, cfg: ConfigPipelineRequestModel = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    if not os.path.exists(os.path.join(project_loc, 'models', model)):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Model [{}] not found".format(model)}
    try:
        with open(os.path.join(project_loc, 'models', model, 'customs', train, '{}.config'.format(train)), 'w') as pipeline_conf:
            pipeline_conf.write(cfg.config)
        return {'message': 'Set new config'}
    except:
        return {'message': 'Cannot edit config'}


@router.post("/start-train/{pid}/{model}/{train}")
def start_train(pid: str, model: str, train: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    try:
        pipeline_config_path = os.path.join(
            project_loc, 'models', model, 'customs', train, "{}.config".format(train))
        print(pipeline_config_path)
        job = mlJob.train_model.delay(os.path.join(project_loc, 'models', model, 'customs', train), pipeline_config_path
                                      )
        return {"jobId": job.id}
    except:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Cannot start training job"}


@router.post("/export/{pid}/{model}/{train}")
def export_model(pid: str, model: str, train: str, response: Response):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    try:
        job = mlJob.export_model.delay(os.path.join(project_loc, 'models', model, 'customs', train),
                                       os.path.join(
                                           project_loc, 'models', model, 'customs', train, "{}.config".format(train)),
                                       os.path.join(project_loc, 'models', model, 'customs', train, 'exported_model'))
        return {"jobId": job.id}
    except:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Cannot export model"}


@router.post("/infer/{pid}/{model}/{train}")
def infer(pid: str, model: str, train: str, response: Response, params: InferenceRequestModel = Body(...)):
    project_loc = os.path.join(config['storage'], pid)
    if not os.path.exists(project_loc):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "Project [{}] did not exist".format(pid)}
    # try:
    mlJob.inference_model.delay(
        os.path.join(project_loc, 'models', model,
                     'customs', train, 'exported_model', 'saved_model'),
        os.path.join(project_loc, 'data', params.label_map_dir),
        os.path.join(project_loc, 'data', params.input_dir),
        os.path.join(project_loc, 'data', params.output_dir))
    return {"message": "Done"}
# except:
    #    response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    #    return {"message": "Cannot infer from model"}
