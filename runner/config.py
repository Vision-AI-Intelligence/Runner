import json


class Config:
    __instance = None

    @staticmethod
    def get_instance():
        if Config.__instance == None:
            Config()
        return Config.__instance

    def get_config(self):
        return self.config

    def __init__(self) -> None:

        if Config.__instance == None:
            with open("./config.json", "r") as config_file:
                self.config = json.loads(config_file.read())
            Config.__instance = self
