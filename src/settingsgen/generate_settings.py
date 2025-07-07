import os
import inspect
import logging

from typing import get_type_hints, get_origin, get_args, List, Optional

from settings_types import RootSchema
from type_generator import smart_schema_update
from logger_configs import logger

logger = logging.getLogger('rl_commons.settingsgen')


def is_dataclass_type(type_hint):
    return inspect.isclass(type_hint) and hasattr(type_hint, "__dataclass_fields__")


def generate_properties(cls, accessor="root_schema", level=1):
    indent = "    " * level
    type_hints = get_type_hints(cls)

    props_code = ""
    for field_name, field_type in type_hints.items():
        real_type = field_type

        if get_origin(field_type) in {list, List, Optional}:
            real_type = get_args(field_type)[0]

        if is_dataclass_type(real_type):
            props_code += f"\n{indent}@property\n"
            props_code += f"{indent}def {field_name}(self) -> {real_type.__name__}:\n"
            # props_code += f"{indent}    return {real_type.__name__}(**self.{accessor}.{field_name})\n"
            props_code += f"{indent}    return self.{accessor}.{field_name}\n"

    return props_code


def generate_app_settings(code):
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    settings_yaml_filepath = os.path.join(root, "settings.yaml")
    settings_types_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings_types.py')
    if not os.path.exists(settings_yaml_filepath):
        with open(settings_yaml_filepath, 'w') as settings_file:
            base_content = '# Generated settings.yaml\n\nmode: "development"'
            settings_file.write(base_content)

    # Convert the `settings.yaml` to dataclasses (types) if necessary
    is_schema_updated = smart_schema_update(settings_yaml_filepath, settings_types_filepath)
    
    if is_schema_updated:
        queue = [("root_schema", RootSchema)]

        while queue:
            accessor, current_cls = queue.pop(0)

            props = generate_properties(current_cls, accessor=accessor)
            code += props

            type_hints = get_type_hints(current_cls)
            for field_name, field_type in type_hints.items():
                real_type = field_type

                if get_origin(field_type) in {list, List, Optional}:
                    real_type = get_args(field_type)[0]

                if is_dataclass_type(real_type):
                    queue.append((f"{accessor}.{field_name}", real_type))

        settings_path = os.path.join(os.path.dirname(__file__), "application_settings.py")
        code = f"{code}\n\n__settings__ = AppSettings()"
        code = f"{code}\nloaded_settings = Configurator()"
        with open(settings_path, "w") as settings_file:
            settings_file.write(code)

        logger.info("Settings exported")
    else:
        logger.warning("No settings exported")

if __name__ == "__main__":
    
    # Default code for the application settings, in case the yaml settings are empty, 
    # This content will still be written into the `application_settings.py`
    default_code = '''
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
        self.path = os.getenv("SETTINGS_PATH", "../../../settings.yaml")

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
'''
    
    generate_app_settings(default_code)