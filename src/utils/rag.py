import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store():
    embeddings = get_embeddings()
    persist_directory = "./chroma_db"
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name="test_scenarios")

def get_retriever():
    vs = get_vector_store()
    return vs.as_retriever(search_kwargs={"k": 5})
