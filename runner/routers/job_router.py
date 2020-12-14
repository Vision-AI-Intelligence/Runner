from fastapi import APIRouter, Response
from runner.background_job import BackgroundJob
router = APIRouter()


@router.post('/revoke/{job_id}')
def revoke(job_id: str):
    BackgroundJob.get_instance().revoke_job(job_id)
    return {"message": "Revoking [{}]".format(job_id)}
