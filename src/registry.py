# src/registry.py
import importlib
import yaml
from src.api.adapters.base_adapter import BaseAdapter

def load_adapters(config_path: str = "config.yaml") -> dict[str, BaseAdapter]:
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    adapters: dict[str, BaseAdapter] = {}
    for name, module_path in cfg["channels"].items():
        module = importlib.import_module(module_path)
        cls = getattr(module, f"{name.capitalize()}Adapter")
        adapters[name] = cls()
    return adapters
