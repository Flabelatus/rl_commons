
"""
    The settings are automatically generated from the dataclasses 
    (settings types and properties)
    app_settings.py <--- generated_dataclasses.py <--- settings.yaml
"""

import os

from ruamel.yaml import YAML
from .settings_types import *
from dacite import from_dict


class Configurator:
    def __init__(self):
        self.yaml = YAML()
        self.path = os.getenv("SETTINGS_PATH", "../../settings.yaml")

    @property
    def general_settings(self):
        path = self.path
        try:
            open(self.path)
        except FileNotFoundError:
            path = os.path.join("..", self.path)
        
        with open(path, "r") as settings_yml:
            settings_data = self.yaml.load(settings_yml)
        settings = from_dict(data_class=RootSchema, data=settings_data)

        return settings
    
    @property
    def mode(self):
        return self.general_settings.mode


class AppSettings(Configurator):
    def __init__(self):
        super().__init__()

    @property
    def root_schema(self) -> RootSchema:
        return self.general_settings


__settings__ = AppSettings()
loaded_settings = Configurator()