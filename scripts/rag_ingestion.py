import os
import sys
import csv
from pathlib import Path

# Add the root directory to sys.path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.rag import get_vector_store
from langchain_core.documents import Document
from src.utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    logger.info("Starting RAG ingestion pipeline...")
    
    data_path = Path(__file__).parent.parent / "data" / "rag_samples" / "sample_test_cases.csv"
    
    if not data_path.exists():
        logger.error(f"Sample data not found at {data_path}")
        return
        
    docs = []
    current_test_case = None
    
    with open(data_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("Title", "").strip()
            if title:
                # Save previous test case if exists
                if current_test_case:
                    content = f"Scenario Title: {current_test_case['title']}\nTags: {current_test_case['tags']}\nSteps:\n" + "\n".join(current_test_case['steps'])
                    metadata = {"type": current_test_case['tags']}
                    docs.append(Document(page_content=content, metadata=metadata))
                
                current_test_case = {
                    "title": title,
                    "tags": row.get("Tags", ""),
                    "steps": []
                }
            
            # Append step to current test case
            if current_test_case:
                step_text = f"- Action: {row.get('Test Step', '')} | Expected: {row.get('Step Expected', '')}"
                current_test_case["steps"].append(step_text)
                
        # Save the last test case
        if current_test_case:
            content = f"Scenario Title: {current_test_case['title']}\nTags: {current_test_case['tags']}\nSteps:\n" + "\n".join(current_test_case['steps'])
            metadata = {"type": current_test_case['tags']}
            docs.append(Document(page_content=content, metadata=metadata))
            
    if docs:
        logger.info(f"Adding {len(docs)} documents to ChromaDB...")
        vs = get_vector_store()
        vs.add_documents(docs)
        logger.info("Ingestion complete.")
    else:
        logger.info("No documents to ingest.")

if __name__ == "__main__":
    ingest_data()
