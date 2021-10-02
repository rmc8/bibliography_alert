import os

import yaml


class YamlConfig:
    def __init__(self, file_path: str = "./settings/config.yml"):
        self.file_path = file_path
    
    def exists(self) -> bool:
        return os.path.exists(self.file_path)
    
    def load(self) -> dict:
        """
        :return: Return yaml data as dictionary format
        """
        with open(self.file_path, "r", encoding="utf-8") as yf:
            return yaml.load(yf, Loader=yaml.FullLoader)
    
    def write(self, data: dict) -> None:
        """
        Export yaml
        :param data: A dictionary of data that will be output in Yaml format
        """
        with open(self.file_path, "w", encoding="utf-8") as yf:
            yaml.dump(data, yf, default_flow_style=False)
