import argparse
import sys
from dotenv import load_dotenv
from src.agent import build_agent
from src.utils.logger import logger
from pathlib import Path

from datetime import datetime

def write_file(filepath: str, content: str):
    path = Path(filepath)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    load_dotenv()
    logger.info("Test Case Generator Agent initialized.")
    
    parser = argparse.ArgumentParser(description="Test Case Generator Agent")
    parser.add_argument("--input", required=True, help="Path to Swagger JSON/YAML or Bruno file")
    parser.add_argument("--output", default=None, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"data/outputs/generated_test_cases_{timestamp}.csv"
    
    logger.info(f"Building LangGraph workflow...")
    app = build_agent()
    
    logger.info(f"Starting execution for input file: {args.input}")
    
    initial_state = {
        "file_path": args.input,
        "api_spec": {},
        "scenarios": [],
        "test_cases": [],
        "final_csv": "",
        "errors": []
    }
    
    final_state = app.invoke(initial_state)
    
    if final_state.get("errors"):
        logger.error("Errors encountered during generation:")
        for err in final_state["errors"]:
            logger.error(f"- {err}")
            print(f"Error: {err}")
            
    if final_state.get("final_csv"):
        write_file(args.output, final_state["final_csv"])
        logger.info(f"Successfully wrote CSV test cases to {args.output}")
        print(f"Successfully wrote CSV test cases to {args.output}")
        
    if final_state.get("java_scripts"):
        scripts_dir = Path("data/outputs/scripts")
        scripts_dir.mkdir(parents=True, exist_ok=True)
        java_output_path = scripts_dir / f"ApiTests_{timestamp}.java"
        write_file(str(java_output_path), final_state["java_scripts"])
        logger.info(f"Successfully wrote Java test scripts to {java_output_path}")
        print(f"Successfully wrote Java test scripts to {java_output_path}")
        
    if not final_state.get("final_csv") and not final_state.get("java_scripts"):
        logger.warning("No output generated.")
        print("No output generated.")

if __name__ == "__main__":
    main()
