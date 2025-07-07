# RL_COMMONS

**RL_COMMONS** is a Python package developed by Javid Jooshesh for the Robot Lab developers team that generates a typed `application_settings.py` file from a root-level `settings.yaml` configuration. It enables Python projects to safely access configuration data as structured, typed settings.

---

## 🚀 Features

- ✅ Load `settings.yaml` from the project root
- ✅ Generate a `@dataclass`-based `application_settings.py` for type-safe access
- ✅ Easy integration with your existing code
- ✅ CLI-based generation (`generate-settings`) for manual or automated workflows

---

## 📦 Installation

Install via `pip`:

```bash
pip install .
```

Or for the editable development 
```bash 
pip install -e .
```
---

## ⚙️ Usage
1.	Place your settings.yaml file at the root of your project.

2.	Run the generator:
```bash
generate-settings
```

3.	Use the generated settings in your code:
```python
from settingsgen import application_settings

print(application_settings.__settings__)  # example usage
```

## 📁 Project Structure
```
rl_commons/
├── pyproject.toml
├── settings.yaml
├── src/
│   └── settingsgen/
│       ├── __init__.py
│       ├── application_settings.py  ← auto-generated
│       ├── generate_settings.py
│       ├── logger_configs.py
│       ├── settings_types.py
│       ├── type_generator.py
│       └── yaml_to_dataclass.py
```

## 🧠 How It Works

•	`settings.yaml` is parsed.
•	A corresponding `application_settings.py` is generated using dataclasses for strongly typed access.
•	You can import it directly once generated.

## 📜 License
MIT License

## 🙌 Contributing
Pull requests and issues are welcome. If you’d like to add features, refactor logic, or improve documentation, feel free to open a discussion.


## 🗣️ Author
Created with ❤️ by Javid Jooshesh
j.jooshesh@hva.nl