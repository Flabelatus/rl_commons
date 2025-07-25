import logging
from ruamel.yaml import YAML
from typing import Dict, List, Any, Set

logger = logging.getLogger('rl_commons.settingsgen')


def convert_to_camel_case(snake_str: str) -> str:
    """Convert a snake_case string to CamelCase."""
    components = snake_str.split('_')
    return ''.join(x.capitalize() for x in components)


def infer_type(value: Any, key: str = None) -> str:
    """Infers the type of a value for the dataclass."""
    if isinstance(value, str):
        return 'str'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, bool):
        return 'bool'
    elif isinstance(value, list):
        if value and isinstance(value[0], dict):
            return f'List[{convert_to_camel_case(key or "Item")}]'
        elif value:
            return f'List[{infer_type(value[0])}]'
        else:
            return 'List[Any]'
    elif isinstance(value, dict):
        if not value:  # Empty dict
            return 'Optional[Any]'
        else:
            return convert_to_camel_case(key or 'NestedClass')
    else:
        return 'Any'


def extract_dependencies(data: Dict[str, Any]) -> Set[str]:
    """Extracts the list of nested class names required for this dictionary."""
    dependencies = set()
    for key, value in data.items():
        if isinstance(value, (dict)):
            dependencies.add(convert_to_camel_case(key))
            dependencies.update(extract_dependencies(value))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            dependencies.add(convert_to_camel_case(key))
            dependencies.update(extract_dependencies(value[0]))
    return dependencies


def generate_dataclass_code(class_name: str, data: Dict[str, Any]) -> str:
    """Generate the Python dataclass code for the given class name and data."""
    lines = [f'@dataclass']
    lines.append(f'class {class_name}:')
    if not data:
        lines.append('    pass')
        return '\n'.join(lines)

    for key, value in data.items():
        if isinstance(value, dict) and value:
            nested_class_name = convert_to_camel_case(key)
            lines.append(f'    {key}: {nested_class_name}')
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            nested_class_name = convert_to_camel_case(key)
            lines.append(f'    {key}: List[{nested_class_name}]')
        else:
            value_type = infer_type(value, key)
            lines.append(f'    {key}: {value_type}')

    return '\n'.join(lines)


def generate_dataclasses_from_yaml(data: Dict[str, Any], parent_class_name: str = 'RootSchema') -> str:
    """Recursively generates dataclasses from a YAML-like dictionary."""
    all_classes = {}
    class_dependencies = {}
    
    def recursive_generate_classes(class_name: str, sub_data: Dict[str, Any]):
        """Recursively generate the classes for all substructures."""
        nonlocal all_classes
        if class_name in all_classes:
            return  # Class already generated
        
        class_code = generate_dataclass_code(class_name, sub_data)
        all_classes[class_name] = class_code
        
        dependencies = extract_dependencies(sub_data)
        class_dependencies[class_name] = dependencies
        
        for key, value in sub_data.items():
            if isinstance(value, (dict)):
                nested_class_name = convert_to_camel_case(key)
                recursive_generate_classes(nested_class_name, value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                nested_class_name = convert_to_camel_case(key)
                recursive_generate_classes(nested_class_name, value[0])
    
    recursive_generate_classes(parent_class_name, data)
    
    # Topological sort of classes to ensure dependencies are met
    sorted_classes = topological_sort(class_dependencies)
    
    comments = '"""\nThe dataclasses are automatically generated from the given yaml schema\n"""\n'
    imports = 'from dataclasses import dataclass\nfrom typing import List, Optional, Any\n\n'
    
    return comments + imports + '\n\n'.join(all_classes[class_name] for class_name in sorted_classes if class_name in all_classes)


def topological_sort(dependencies: Dict[str, Set[str]]) -> List[str]:
    """Sorts the classes according to their dependencies so that all required classes are defined before they are used."""
    sorted_classes = []
    visited = set()
    
    def visit(class_name):
        if class_name not in visited:
            visited.add(class_name)
            for dep in dependencies.get(class_name, []):
                visit(dep)
            sorted_classes.append(class_name)
    
    for class_name in dependencies:
        visit(class_name)
    
    return sorted_classes


def convert_commented_map_to_dict(data):
    """Recursively convert ruamel.yaml CommentedMap to a Python dict."""
    if isinstance(data, dict):
        return {key: convert_commented_map_to_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_commented_map_to_dict(item) for item in data]
    else:
        return data


def generate_dataclass_file(yaml_path: str, output_path: str = 'generated_dataclasses.py'):
    """Main function to generate the dataclasses file from a YAML file."""
    yaml = YAML()
    with open(yaml_path, 'r') as file:
        parsed_yaml = yaml.load(file)
    
    # Convert CommentedMap to a regular Python dict
    parsed_yaml = convert_commented_map_to_dict(parsed_yaml)
    
    # Generate the dataclass code
    dataclass_code = generate_dataclasses_from_yaml(parsed_yaml)

    logger.debug(f"Dataclass file generated at: {output_path}")

    return dataclass_code