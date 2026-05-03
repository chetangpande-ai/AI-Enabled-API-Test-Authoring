import os
import hashlib
from typing import Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from src.utils.logger import logger

# EnsembleRetriever implementation for hybrid search
class EnsembleRetriever:
    """Simple ensemble retriever combining multiple retrievers"""
    def __init__(self, retrievers, weights):
        self.retrievers = retrievers
        self.weights = weights
    
    def invoke(self, query):
        """Combine results from multiple retrievers weighted by importance"""
        all_docs = {}
        
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)
            for doc in docs:
                doc_key = doc.page_content[:100]  # Use content as key
                if doc_key not in all_docs:
                    all_docs[doc_key] = {"doc": doc, "score": 0}
                all_docs[doc_key]["score"] += weight
        
        # Sort by combined score and return
        sorted_docs = sorted(all_docs.values(), key=lambda x: x["score"], reverse=True)
        return [item["doc"] for item in sorted_docs]

def get_embeddings():
    """Get HuggingFace embeddings"""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(collection_name="test_scenarios"):
    """Get ChromaDB vector store"""
    embeddings = get_embeddings()
    persist_directory = "./chroma_db"
    return Chroma(
        persist_directory=persist_directory, 
        embedding_function=embeddings, 
        collection_name=collection_name
    )

def get_retriever(collection_name="test_scenarios", k=5):
    """Standard semantic retriever (legacy)"""
    vs = get_vector_store(collection_name)
    return vs.as_retriever(search_kwargs={"k": k})

def get_hybrid_retriever(docs: list[Document] = None, collection_name="test_scenarios", k=5):
    """
    Hybrid retriever combining semantic search (ChromaDB) + lexical search (BM25)
    
    Args:
        docs: Optional list of documents for BM25 (if None, uses all from vector store)
        collection_name: ChromaDB collection name
        k: Number of results to return
    
    Returns:
        EnsembleRetriever combining both search methods
    """
    # Semantic retriever (ChromaDB)
    semantic_retriever = get_vector_store(collection_name).as_retriever(
        search_kwargs={"k": k}
    )
    
    # Lexical retriever (BM25)
    if docs:
        lexical_retriever = BM25Retriever.from_documents(docs)
    else:
        # Get docs from ChromaDB if not provided
        vs = get_vector_store(collection_name)
        all_docs = vs.get()
        if all_docs.get("documents"):
            docs = [
                Document(
                    page_content=doc,
                    metadata=meta
                )
                for doc, meta in zip(all_docs["documents"], all_docs.get("metadatas", []))
            ]
            lexical_retriever = BM25Retriever.from_documents(docs)
        else:
            logger.warning("No documents found for BM25 retriever")
            return semantic_retriever
    
    # Ensemble: weight 0.5 for each
    ensemble_retriever = EnsembleRetriever(
        retrievers=[semantic_retriever, lexical_retriever],
        weights=[0.5, 0.5]
    )
    
    return ensemble_retriever

def calculate_scenario_fingerprint(scenario: dict) -> str:
    """
    Calculate a fingerprint for a scenario to detect exact duplicates
    
    Args:
        scenario: Dictionary with keys like 'name', 'description', 'type'
    
    Returns:
        SHA256 hash as fingerprint
    """
    # Normalize text: lowercase, strip whitespace
    content = f"{scenario.get('name', '').lower().strip()}|{scenario.get('description', '').lower().strip()}|{scenario.get('type', '').lower().strip()}"
    return hashlib.sha256(content.encode()).hexdigest()

def calculate_content_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings using Jaccard similarity
    
    Args:
        text1, text2: Text to compare
    
    Returns:
        Similarity score between 0 and 1
    """
    # Tokenize and create sets of words
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    # Jaccard similarity
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0

def filter_duplicate_scenarios(
    new_scenarios: list[dict],
    existing_docs: list[Document] = None,
    similarity_threshold: float = 0.7
) -> tuple[list[dict], list[dict]]:
    """
    Filter out scenarios that are duplicates or too similar to existing ones
    
    Args:
        new_scenarios: List of new scenarios to check
        existing_docs: List of existing documents from RAG
        similarity_threshold: Minimum similarity score to consider as duplicate (0-1)
    
    Returns:
        Tuple of (unique_scenarios, duplicate_scenarios)
    """
    if not existing_docs:
        return new_scenarios, []
    
    unique_scenarios = []
    duplicate_scenarios = []
    seen_fingerprints = set()
    
    # Extract existing scenario content
    existing_content = [doc.page_content for doc in existing_docs]
    
    for scenario in new_scenarios:
        fingerprint = calculate_scenario_fingerprint(scenario)
        scenario_text = f"{scenario.get('name', '')} {scenario.get('description', '')}"
        
        # Check exact duplicate (same fingerprint)
        if fingerprint in seen_fingerprints:
            logger.warning(f"Duplicate scenario detected (fingerprint): {scenario.get('name')}")
            duplicate_scenarios.append(scenario)
            continue
        
        # Check similarity with existing scenarios
        is_duplicate = False
        for existing in existing_content:
            similarity = calculate_content_similarity(scenario_text, existing)
            if similarity >= similarity_threshold:
                logger.warning(
                    f"Similar scenario detected: '{scenario.get('name')}' "
                    f"(similarity: {similarity:.2f})"
                )
                duplicate_scenarios.append(scenario)
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_scenarios.append(scenario)
            seen_fingerprints.add(fingerprint)
    
    logger.info(
        f"Deduplication: {len(unique_scenarios)} unique, "
        f"{len(duplicate_scenarios)} duplicates from {len(new_scenarios)}"
    )
    
    return unique_scenarios, duplicate_scenarios
