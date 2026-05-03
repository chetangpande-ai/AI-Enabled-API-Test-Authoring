import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.rag import get_vector_store
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.logger import logger
from dotenv import load_dotenv

load_dotenv()

def ingest_framework():
    logger.info("Starting Framework Guidelines ingestion...")
    
    data_path = Path(__file__).parent.parent / "data" / "rag_samples" / "framework_guidelines.md"
    
    if not data_path.exists():
        logger.error(f"Framework guidelines not found at {data_path}")
        return
        
    loader = TextLoader(str(data_path))
    documents = loader.load()
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
            
    if docs:
        logger.info(f"Adding {len(docs)} framework chunks to ChromaDB collection 'framework_guidelines'...")
        vs = get_vector_store("framework_guidelines")
        vs.add_documents(docs)
        logger.info("Ingestion complete.")
    else:
        logger.info("No documents to ingest.")

if __name__ == "__main__":
    ingest_framework()
