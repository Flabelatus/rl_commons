import os
import sys

root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

sys.path.append(root)

try:
    from settingsgen.application_settings import __settings__, loaded_settings
    from settingsgen.logger_configs import logger
except ImportError: 
    pass


# from settingsgen.generate_settings import generate_app_settings


# # Default code for the application settings, in case the yaml settings are empty, 
# # This content will still be written into the `application_settings.py`
# default_code = '''
# """
#     The settings are automatically generated from the dataclasses 
#     (settings types and properties)
#     app_settings.py <--- generated_dataclasses.py <--- settings.yaml
# """

# import os

# from ruamel.yaml import YAML
# from .settings_types import *
# from dacite import from_dict


# class Configurator:
#     def __init__(self):
#         self.yaml = YAML()
#         self.path = os.getenv("SETTINGS_PATH", "../../../settings.yaml")

#     @property
#     def general_settings(self):
#         path = self.path
#         try:
#             open(self.path)
#         except FileNotFoundError:
#             path = os.path.join("..", self.path)
        
#         with open(path, "r") as settings_yml:
#             settings_data = self.yaml.load(settings_yml)
#         settings = from_dict(data_class=RootSchema, data=settings_data)

#         return settings
    
#     @property
#     def mode(self):
#         return self.general_settings.mode


# class AppSettings(Configurator):
#     def __init__(self):
#         super().__init__()

#     @property
#     def root_schema(self) -> RootSchema:
#         return self.general_settings
# '''

# if __name__ == '__main__':
#     generate_app_settings(default_code)