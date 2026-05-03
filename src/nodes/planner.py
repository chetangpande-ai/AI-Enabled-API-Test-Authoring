import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.models.state import AgentState
from src.utils.llm import get_llm
from src.utils.logger import logger
from src.utils.rag import get_retriever
from pydantic import BaseModel, Field

class ScenarioModel(BaseModel):
    name: str = Field(description="Name of the scenario")
    description: str = Field(description="Description of what is being tested")
    type: str = Field(description="Type of test: positive, negative, or edge_case")

class PlannerOutput(BaseModel):
    scenarios: list[ScenarioModel]

def plan_scenarios_node(state: AgentState) -> dict:
    logger.info("Starting plan_scenarios_node")
    if state.get("errors"):
        logger.error("Errors found in state, skipping planner")
        return {}
    
    try:
        spec_str = json.dumps(state.get("api_spec", {}), indent=2)
        
        logger.info("Retrieving existing test scenarios from RAG...")
        retriever = get_retriever()
        docs = retriever.invoke(spec_str)
        context = "\n".join([d.page_content for d in docs])
        logger.debug(f"Retrieved Context: {context}")
        
        llm = get_llm()
        parser = PydanticOutputParser(pydantic_object=PlannerOutput)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert QA Engineer. Analyze the API specification and generate a comprehensive list of NEW test scenarios. You must include positive flows, negative flows, and edge cases.\n\nIMPORTANT: Review the 'Existing Scenarios' provided. DO NOT generate scenarios that are already covered in the Existing Scenarios. Only create scenarios for requirements that are missing.\n\nExisting Scenarios:\n{context}\n\n{format_instructions}"),
            ("user", "API Specification:\n{api_spec}")
        ])
        
        chain = prompt | llm
        
        logger.info("Invoking LLM for scenario planning...")
        response = chain.invoke({
            "api_spec": spec_str,
            "context": context if context else "None",
            "format_instructions": parser.get_format_instructions()
        })
        
        import re
        content = response.content
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match:
            raise ValueError(f"Could not extract JSON from response: {content}")
            
        json_str = match.group(0)
        result = parser.parse(json_str)
        
        scenarios = [{"name": s.name, "description": s.description, "type": s.type} for s in result.scenarios]
        logger.info(f"Planned {len(scenarios)} new scenarios")
        logger.debug(f"Scenarios: {scenarios}")
        
        return {"scenarios": scenarios}
    except Exception as e:
        logger.error(f"Planner Error: {str(e)}", exc_info=True)
        return {"errors": state.get("errors", []) + [f"Planner Error: {str(e)}"]}
