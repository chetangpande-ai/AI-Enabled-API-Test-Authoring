import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(collection_name="test_scenarios"):
    embeddings = get_embeddings()
    persist_directory = "./chroma_db"
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name=collection_name)

def get_retriever(collection_name="test_scenarios", k=5):
    vs = get_vector_store(collection_name)
    return vs.as_retriever(search_kwargs={"k": k})
