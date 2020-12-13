from pydantic import BaseModel


class DatasetPath(BaseModel):
    path_to_annotation: str
    path_to_images: str
    path_to_label_map: str
    path_to_tfrecord: str
