from fastapi import FastAPI

from runner.routers import io_router
from runner.routers import ml_router

app = FastAPI()

app.include_router(io_router.router, prefix='/io')
app.include_router(ml_router.router, prefix='/ml')


@app.get("/")
def read_root():
    return {"Hello": "World"}
