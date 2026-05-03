import json
from langchain_core.prompts import ChatPromptTemplate
from src.models.state import AgentState
from src.utils.llm import get_llm
from src.utils.logger import logger
from src.utils.rag import get_retriever

def script_generator_node(state: AgentState) -> dict:
    logger.info("Starting script_generator_node")
    if state.get("errors") or not state.get("test_cases"):
        logger.warning("Errors found or no test cases available, skipping script generator")
        return {}
    
    try:
        logger.info("Retrieving framework guidelines from RAG...")
        retriever = get_retriever(collection_name="framework_guidelines", k=3)
        docs = retriever.invoke("Java TestNG RestAssured ExtentReports Guidelines")
        guidelines = "\n".join([d.page_content for d in docs])
        logger.debug(f"Retrieved Guidelines: {guidelines}")
        
        llm = get_llm()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Java SDET. Write a complete, modular, and syntax-error-free Java test automation script using TestNG and REST Assured.\n\nYour code MUST strictly follow these Framework Guidelines:\n{guidelines}\n\nReturn ONLY the raw Java code. Do not include markdown code blocks (like ```java) or any introductory text."),
            ("user", "API Specification:\n{api_spec}\n\nTest Cases to Automate:\n{test_cases}")
        ])
        
        chain = prompt | llm
        
        spec_str = json.dumps(state.get("api_spec", {}), indent=2)
        cases_str = json.dumps(state.get("test_cases", []), indent=2)
        
        logger.info("Invoking LLM to generate Java TestNG scripts...")
        response = chain.invoke({
            "api_spec": spec_str,
            "test_cases": cases_str,
            "guidelines": guidelines if guidelines else "No guidelines found."
        })
        
        java_code = response.content
        
        # Clean up possible markdown if LLM includes it anyway
        if java_code.startswith("```java"):
            java_code = java_code.split("```java")[1]
        if java_code.endswith("```"):
            java_code = java_code.rsplit("```", 1)[0]
            
        java_code = java_code.strip()
        
        logger.info("Successfully generated Java scripts")
        return {"java_scripts": java_code}
    except Exception as e:
        logger.error(f"Script Generator Error: {str(e)}", exc_info=True)
        return {"errors": state.get("errors", []) + [f"Script Generator Error: {str(e)}"]}
