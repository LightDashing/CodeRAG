import json
from pathlib import Path

class Config:
    config: dict
    _instance = None

    @staticmethod
    def get_instance():
        if Config._instance is None:
            Config()
        return Config._instance

    def __init__(self):
        if Config._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.config = self.load_config()
            Config._instance = self

    def load_config(self):
        config_path = Path(__file__).parent / 'config.json'  # Adjusted path

        with open(config_path, 'r') as config_file:
            return json.load(config_file)
        
    def write_config(self, config: dict):
        config_path = Path(__file__).parent / 'config.json'  # Adjusted path
        
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        
config = Config.get_instance().config