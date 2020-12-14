from typing import IO
from celery import Celery
from runner.config import Config
import redis
from celery import current_app


class BackgroundJob:
    __instance = None

    @staticmethod
    def get_instance():
        if BackgroundJob.__instance == None:
            BackgroundJob()
        return BackgroundJob.__instance

    def set_status(self, task_id, key, value):
        self.redis_app.hset(task_id, key, value)

    def revoke_job(self, task_id):
        self.redis_app.hset(task_id, 'status', 'revoked')
        current_app.control.revoke(task_id, terminate=True)

    def __init__(self):
        if BackgroundJob.__instance != None:
            print("BackgroundJob has no instance")
        else:
            BackgroundJob.__instance = self
            config = Config.get_instance().get_config()
            endpoint = "redis://redis:{}@{}:{}".format(
                config['redis']['password'], config['redis']['host'], config['redis']['port'])
            self.celery_app = Celery(
                'tasks',
                backend=endpoint,
                broker=endpoint,)
            self.redis_app = redis.Redis(
                host=config['redis']['host'], port=config['redis']['port'], password=config['redis']['password'])
