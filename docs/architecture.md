# Test Case Generator Architecture

This document provides a detailed breakdown of the Test Case Generator Agent's architecture, including its components, data flow, and technologies.

## High-Level Flow Diagram

The following diagram illustrates how an input specification travels through the LangGraph workflow, interacts with the local RAG pipeline, consults the LLM, and results in a final ADO CSV output.

```mermaid
graph TD
    classDef inputNode fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000;
    classDef processNode fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000;
    classDef dbNode fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#000;
    classDef externalNode fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000;
    classDef outputNode fill:#ffebee,stroke:#d32f2f,stroke-width:2px,color:#000;

    %% Data Sources Layer
    subgraph "1. Inputs & Knowledge Base"
        A[📄 Input: Swagger / Bruno API Spec]:::inputNode
        
        subgraph "RAG System"
            B[🗃️ Sample Test Cases (CSV)]:::inputNode -->|Ingested via scripts/rag_ingestion.py| C[(ChromaDB Vector Store)]:::dbNode
        end
    end

    %% Execution Layer
    subgraph "2. LangGraph Execution Pipeline"
        D(🛠️ Parser Node):::processNode
        E(🧠 Planner Node):::processNode
        F(⚙️ Generator Node):::processNode
        G(📋 Formatter Node):::processNode
        
        D -->|Loads Spec| E
        E -->|Provides New Scenarios| F
        F -->|Provides Detailed Steps| G
    end
    
    %% External Services Layer
    subgraph "3. External AI Services"
        H{{🤖 MeshAPI LLM GPT-4}}:::externalNode
    end

    %% Top-Down Flow Connections
    A -->|Feeds Raw Data| D
    C -.->|Injects Existing Scenarios Context| E
    
    E <-->|Queries for Scenarios| H
    F <-->|Queries for Test Steps| H

    %% Final Output
    subgraph "4. Delivery"
        I[📊 Output: ADO Formatted CSV File]:::outputNode
    end

    G -->|Generates Format| I
```

## Component Details

### 1. Inputs
- **API Specification**: The system accepts Swagger/OpenAPI files (JSON or YAML format) or Bruno collections. This defines the requirements (endpoints, payload structures, parameters) for the test cases.

### 2. Retrieval-Augmented Generation (RAG)
The RAG pipeline ensures that the agent does not generate duplicate tests. 
- **Embeddings Model**: We use the local, open-source `all-MiniLM-L6-v2` model from HuggingFace (`sentence-transformers`). This provides semantic search capabilities without relying on external embedding APIs.
- **Vector Database**: **ChromaDB** is used to store the vectorized test cases locally in the `chroma_db/` directory.
- **Retrieval Engine**: When the agent processes a specific API endpoint, the retriever queries ChromaDB to find the 5 most semantically similar existing test scenarios. These are injected into the LLM prompt.

### 3. LangGraph Workflow
The core of the agent is a state machine governed by LangGraph. It passes an `AgentState` object between four specialized nodes.

- **Parser Node**: Reads the local API specification file, resolves its format, and loads the raw data into the agent's memory state.
- **Planner Node**:
  - Takes the parsed API endpoint data.
  - Queries the RAG retriever to fetch existing test scenarios.
  - Formulates a prompt using the API spec and the retrieved context.
  - Instructs the LLM to output a structured JSON list of *only* new, missing test scenarios (Positive, Negative, Edge cases).
- **Generator Node**:
  - Receives the list of new test scenarios.
  - Prompts the LLM to expand each high-level scenario into detailed, step-by-step instructions.
  - Uses `PydanticOutputParser` to ensure the LLM strictly adheres to the required JSON schema.
- **Formatter Node**: 
  - Takes the structured JSON response and converts it into a comma-separated values (CSV) string.
  - Specifically designed to handle Azure DevOps (ADO) quirks, such as merging multi-step test cases into consecutive rows with blank title cells.

### 4. LLM Provider
- **MeshAPI**: The system connects to OpenAI-compatible endpoints hosted on MeshAPI (e.g., `https://api.meshapi.ai/v1`). 
- The LangChain wrapper `ChatOpenAI` is utilized to send and receive structured JSON responses securely.

### 5. Logging System
A comprehensive logging component is built into `src/utils/logger.py`. It tracks:
- Execution paths and node transitions.
- Internal errors or failed parsing events.
- Extracted contexts from the RAG pipeline.
- All logs are streamed to standard output and persisted in datetime-stamped files in the `logs/` directory.
