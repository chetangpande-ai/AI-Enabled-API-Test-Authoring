from langgraph.graph import StateGraph, END
from src.models.state import AgentState
from src.nodes.parser import parse_spec_node
from src.nodes.planner import plan_scenarios_node
from src.nodes.generator import generate_test_cases_node
from src.nodes.formatter import format_csv_node
from src.nodes.script_generator import script_generator_node

def build_agent():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("parse_spec", parse_spec_node)
    workflow.add_node("plan_scenarios", plan_scenarios_node)
    workflow.add_node("generate_test_cases", generate_test_cases_node)
    workflow.add_node("format_csv", format_csv_node)
    workflow.add_node("script_generator", script_generator_node)
    
    workflow.set_entry_point("parse_spec")
    
    workflow.add_edge("parse_spec", "plan_scenarios")
    workflow.add_edge("plan_scenarios", "generate_test_cases")
    
    # Forking after generation: create both CSV and Java Scripts
    workflow.add_edge("generate_test_cases", "format_csv")
    workflow.add_edge("generate_test_cases", "script_generator")
    
    workflow.add_edge("format_csv", END)
    workflow.add_edge("script_generator", END)
    
    app = workflow.compile()
    return app
