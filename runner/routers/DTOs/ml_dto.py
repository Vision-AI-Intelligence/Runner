from pydantic import BaseModel


class DatasetPath(BaseModel):
    path_to_annotation: str
    path_to_images: str
    path_to_label_map: str
    path_to_tfrecord: str


class PretrainedModel(BaseModel):
    url: str
    name: str


class TrainParams(BaseModel):
    model_dir: str
    pipeline_dir: str


class ConfigPipelineRequestModel(BaseModel):
    config: str


class InferenceRequestModel(BaseModel):
    input_dir: str
    output_dir: str
    label_map_dir: str
