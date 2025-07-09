import os
import inspect
import logging

from typing import get_type_hints, get_origin, get_args, List, Optional

# from settings_types import RootSchema
from settingsgen.type_generator import smart_schema_update
from settingsgen.logger_configs import logger
from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class RootSchema:
    mode: str


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


def generate_app_settings(directory_path):
    
    code = '''
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
    def __init__(self, path):
        self.yaml = YAML()
        self.path = path

    @property
    def general_settings(self):
        path = self.path
        try:
            open(self.path)
        except FileNotFoundError:
            pass
        
        with open(os.path.join(path, "settings.yaml"), "r") as settings_yml:
            settings_data = self.yaml.load(settings_yml)
        settings = from_dict(data_class=RootSchema, data=settings_data)

        return settings
    
    @property
    def mode(self):
        return self.general_settings.mode


class AppSettings(Configurator):
    def __init__(self, path):
        super().__init__(path=path)

    @property
    def root_schema(self) -> RootSchema:
        return self.general_settings
'''
    
    root = os.path.abspath(directory_path)

    settings_yaml_filepath = os.path.join(root, "settings.yaml")
    settings_types_filepath = os.path.join(root, 'settings', 'settings_types.py')
    if not os.path.exists(settings_types_filepath):
        os.mkdir(os.path.join(root, 'settings'))
        with open(settings_types_filepath, 'w') as settings_types_file:
            content = '# Generated settings_types file'
            settings_types_file.write(content)

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

        settings_path = os.path.join(root, 'settings', 'application_settings.py')
        code = f"{code}\n\n__settings__ = AppSettings('{root}')"
        code = f"{code}\nloaded_settings = Configurator('{root}')"
        with open(settings_path, "w") as settings_file:
            settings_file.write(code)

        logger.info("Settings exported")
    else:
        logger.warning("No settings exported")
