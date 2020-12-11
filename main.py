from typing import Optional

from fastapi import FastAPI

from runner.job import ioJob
from runner.routers import io_router

app = FastAPI()

app.include_router(io_router.router, prefix='/io')


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/add/{a}/{b}")
def add(a: float, b: float):
    result = ioJob.add.delay(a, b)
    return result.get(timeout=1)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
