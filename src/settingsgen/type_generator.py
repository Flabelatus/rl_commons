import logging
import ast
import os
from settingsgen.logger_configs import logger
from settingsgen.yaml_to_dataclass import generate_dataclass_file
import settingsgen.settings_types as st

logger = logging.getLogger('rl_commons.settingsgen')


def extract_summary(source_code: str):
    tree = ast.parse(source_code)
    classes = {}
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
        elif isinstance(node, ast.ClassDef):
            method_names = []
            attributes = {}
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef):
                    method_names.append(stmt.name)
                elif isinstance(stmt, ast.AnnAssign):  # Annotated assignment (typed field)
                    if isinstance(stmt.target, ast.Name):
                        field_name = stmt.target.id
                        field_type = ast.unparse(stmt.annotation)
                        attributes[field_name] = field_type
                elif isinstance(stmt, ast.Assign):  # Unannotated assignment
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            field_name = target.id
                            attributes[field_name] = 'Any'  # No type info available

            classes[node.name] = {
                'methods': sorted(method_names),
                'attributes': attributes,
            }

    return {
        'imports': sorted(imports),
        'classes': classes,
    }


def should_save_file(existing_content: str, new_content: str) -> bool:
    existing_summary = extract_summary(existing_content) if existing_content else None
    new_summary = extract_summary(new_content)

    if not existing_summary:
        return True  # File doesn't exist

    # Compare imports
    if existing_summary['imports'] != new_summary['imports']:
        return True

    # Compare class names
    if set(existing_summary['classes'].keys()) != set(new_summary['classes'].keys()):
        return True
    
    # Compare methods and attributes inside classes
    for cls in existing_summary['classes']:
        old_class = existing_summary['classes'][cls]
        new_class = new_summary['classes'].get(cls)
        if not new_class:
            return True

        if old_class['methods'] != new_class['methods']:
            return True

        old_attrs = old_class['attributes']
        new_attrs = new_class['attributes']

        if old_attrs.keys() != new_attrs.keys():
            return True

        for attr_name in old_attrs:
            if old_attrs[attr_name] != new_attrs[attr_name]:
                return True
            
    return False


def smart_save_python_file(filepath: str, new_content: str):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            existing_content = f.read()
    else:
        existing_content = ""

    if should_save_file(existing_content, new_content):
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    else:
        return False

def smart_schema_update(src_path: str, dist_path: str):
    """Convert the contents of the settings.yaml file into dataclasses to have the type
    references to each field of the settings
    """
    keys = []
    for element in dir(st):
        if element.startswith("_") or element.endswith("_"):
            continue
        keys.append(element)

    # Generate the new code to compare
    new_generated_code = generate_dataclass_file(src_path, dist_path)

    # Save the file only if the contents of the new code are changed in a meaningful 
    # way, otherwise, do not write the contents to file. As the settings_types.py is 
    # tracked by Git.
    is_saved = smart_save_python_file(dist_path, new_generated_code)
    if is_saved:
        logger.info('The settings types schema updated successfully at `settings_types.py`')
    else:
        logger.warning('No new changes in schema detected')
    
    return is_saved