import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models.state import AgentState
from src.utils.llm import get_llm
from src.utils.logger import logger
from pydantic import BaseModel, Field

class TestCaseModel(BaseModel):
    name: str
    scenario_type: str
    description: str
    steps: list[str] = Field(description="Step by step instructions")
    expected_result: str

class GeneratorOutput(BaseModel):
    test_cases: list[TestCaseModel]

def generate_test_cases_node(state: AgentState) -> dict:
    logger.info("Starting generate_test_cases_node")
    if state.get("errors") or not state.get("scenarios"):
        logger.warning("Errors found or no scenarios available, skipping generator")
        return {}
    
    try:
        llm = get_llm()
        parser = PydanticOutputParser(pydantic_object=GeneratorOutput)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert QA Automation Engineer. Based on the API specification and the test scenarios, generate detailed, step-by-step test cases. Include the request details (method, endpoint, payload) in the steps, and state the expected outcome clearly.\n\n{format_instructions}"),
            ("user", "API Specification:\n{api_spec}\n\nScenarios to cover:\n{scenarios}")
        ])
        
        chain = prompt | llm
        
        spec_str = json.dumps(state.get("api_spec", {}), indent=2)
        scenarios_str = json.dumps(state.get("scenarios", []), indent=2)
        
        logger.info(f"Invoking LLM to generate test cases for {len(state.get('scenarios', []))} scenarios...")
        response = chain.invoke({
            "api_spec": spec_str, 
            "scenarios": scenarios_str,
            "format_instructions": parser.get_format_instructions()
        })
        
        import re
        content = response.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not extract JSON from response: {content}")
            
        json_str = match.group(0)
        result = parser.parse(json_str)
        
        test_cases = [
            {
                "name": tc.name,
                "scenario_type": tc.scenario_type,
                "description": tc.description,
                "steps": tc.steps,
                "expected_result": tc.expected_result
            } for tc in result.test_cases
        ]
        
        logger.info(f"Generated {len(test_cases)} detailed test cases")
        return {"test_cases": test_cases}
    except Exception as e:
        logger.error(f"Generator Error: {str(e)}", exc_info=True)
        return {"errors": state.get("errors", []) + [f"Generator Error: {str(e)}"]}
