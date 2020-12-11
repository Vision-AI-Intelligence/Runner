from typing import IO
from celery import Celery
from runner.config import Config


class BackgroundJob:
    __instance = None

    @staticmethod
    def get_instance():
        if BackgroundJob.__instance == None:
            BackgroundJob()
        return BackgroundJob.__instance

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
