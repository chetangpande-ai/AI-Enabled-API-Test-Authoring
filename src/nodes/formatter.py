import csv
import io
from src.models.state import AgentState
from src.utils.logger import logger

def format_csv_node(state: AgentState) -> dict:
    logger.info("Starting format_csv_node")
    if state.get("errors"):
        logger.error("Errors found in state, skipping CSV generation")
        return {}
        
    test_cases = state.get("test_cases", [])
    if not test_cases:
        logger.warning("No test cases to format")
        return {"final_csv": "ID,Work Item Type,Title,Test Step,Step Expected\n"}
        
    logger.info(f"Formatting {len(test_cases)} test cases into ADO CSV format")
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(["ID", "Work Item Type", "Title", "Test Step", "Step Expected", "Tags"])
    
    for tc in test_cases:
        title = tc["name"]
        tags = tc["scenario_type"]
        
        steps = tc.get("steps", [])
        expected_result = tc.get("expected_result", "")
        
        if not steps:
            writer.writerow(["", "Test Case", title, "Execute test", expected_result, tags])
            continue
            
        for i, step in enumerate(steps):
            if i == 0:
                writer.writerow(["", "Test Case", title, step, expected_result if len(steps) == 1 else "", tags])
            elif i == len(steps) - 1:
                writer.writerow(["", "Test Case", "", step, expected_result, ""])
            else:
                writer.writerow(["", "Test Case", "", step, "", ""])

    csv_content = output.getvalue()
    logger.info("CSV generation complete")
    return {"final_csv": csv_content}
