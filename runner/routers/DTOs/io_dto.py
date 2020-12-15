from typing import Optional
from pydantic import BaseModel


class DeletedFile(BaseModel):
    filename: str


class DownloadedFile(BaseModel):
    url: str
    filename: str
    section: Optional[str] = 'data'


class UnzippedFile(BaseModel):
    filename: str
