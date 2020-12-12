from pydantic import BaseModel


class DeletedFile(BaseModel):
    filename: str


class DownloadedFile(BaseModel):
    url: str
    filename: str


class UnzippedFile(BaseModel):
    filename: str
