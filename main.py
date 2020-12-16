from fastapi import FastAPI

from runner.routers import io_router
from runner.routers import ml_router
from runner.routers import job_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=['*'],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)

app.include_router(io_router.router, prefix='/io')
app.include_router(ml_router.router, prefix='/ml')
app.include_router(job_router.router, prefix='/job')


@app.get("/")
def read_root():
    return {"Hello": "World"}
