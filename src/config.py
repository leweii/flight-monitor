# src/config.py
import os
import re
import yaml
from pathlib import Path

def expand_env_vars(value: str) -> str:
    """Expand ${VAR:-default} syntax in string values."""
    pattern = r'\$\{([^}]+)\}'

    def replacer(match):
        var_expr = match.group(1)
        if ':-' in var_expr:
            var_name, default = var_expr.split(':-', 1)
        else:
            var_name, default = var_expr, ''
        return os.environ.get(var_name, default)

    return re.sub(pattern, replacer, value)

def process_config(obj):
    """Recursively expand environment variables in config."""
    if isinstance(obj, dict):
        return {k: process_config(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [process_config(item) for item in obj]
    elif isinstance(obj, str):
        return expand_env_vars(obj)
    return obj

def load_config(path: str = None) -> dict:
    """Load and process configuration file."""
    if path is None:
        path = Path(__file__).parent.parent / "config.yaml"

    with open(path) as f:
        config = yaml.safe_load(f)

    return process_config(config)
