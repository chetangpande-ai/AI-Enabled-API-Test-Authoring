import json
import yaml
from pathlib import Path
from src.models.state import AgentState
from src.utils.logger import logger

def parse_spec_node(state: AgentState) -> dict:
    logger.info("Starting parse_spec_node")
    file_path = state.get("file_path")
    if not file_path:
        logger.error("No file_path provided in state")
        return {"errors": state.get("errors", []) + ["No file_path provided"]}
    
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return {"errors": state.get("errors", []) + [f"File not found: {file_path}"]}
    
    logger.info(f"Parsing API spec from {file_path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix == '.json':
                data = json.load(f)
            elif path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = {"raw_content": f.read()}
        logger.info("Successfully parsed API spec")
        return {"api_spec": data}
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        return {"errors": state.get("errors", []) + [str(e)]}
