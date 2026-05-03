import json
import yaml
from pathlib import Path
from typing import Dict, Any

def read_file(filepath: str) -> Dict[str, Any]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(path, 'r', encoding='utf-8') as f:
        if path.suffix == '.json':
            return json.load(f)
        elif path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file extension: {path.suffix}")

def write_markdown(filepath: str, content: str):
    path = Path(filepath)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
