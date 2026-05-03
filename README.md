# Test Case Generator Agent

The **Test Case Generator Agent** is an AI-powered tool built with [LangChain](https://python.langchain.com/) and [LangGraph](https://python.langchain.com/docs/langgraph/). It analyzes API specifications (like Swagger JSON/YAML) and automatically generates comprehensive test cases formatted for direct import into **Azure DevOps (ADO)**.

## Features

- **Automated Test Planning**: Uses GPT-4 to brainstorm positive, negative, and edge-case scenarios based on the provided API endpoints.
- **Detailed Test Case Generation**: Translates high-level scenarios into step-by-step executable test cases with expected results.
- **ADO CSV Output**: Automatically formats the output into Azure DevOps CSV format, handling multi-step test cases correctly (blank titles for subsequent steps).
- **RAG for Context**: Uses a local **ChromaDB** vector database to store and retrieve existing test scenarios. This prevents the agent from generating duplicate scenarios and ensures it focuses only on new/missing requirements.
- **Comprehensive Logging**: Automatically logs all steps, LLM inputs/outputs, and RAG contexts into timestamped files in the `logs/` directory.

## Project Architecture

The agent is built as a state machine using LangGraph. The workflow consists of four main nodes:

1. **Parser** (`src/nodes/parser.py`): Reads the API specification file into the agent state.
2. **Planner** (`src/nodes/planner.py`): Queries ChromaDB for existing test scenarios related to the API. It then injects these into the LLM prompt, asking the LLM to generate *only* new missing scenarios.
3. **Generator** (`src/nodes/generator.py`): Takes the planned scenarios and asks the LLM to write detailed step-by-step instructions.
4. **Formatter** (`src/nodes/formatter.py`): Converts the structured Python dictionaries into the final ADO CSV string.

```text
/
├── chroma_db/                  # Local vector database storage
├── docs/                       # Project documentation
├── logs/                       # Execution logs
├── data/                       # Dedicated folder for all data
│   ├── inputs/                 # Raw API Specs (Swagger/Bruno)
│   ├── outputs/                # Generated ADO CSV Test Cases
│   └── rag_samples/            # Seed data for vector database
├── scripts/                    # Dedicated folder for standalone scripts
│   └── rag_ingestion.py        # Script to ingest sample test cases into ChromaDB
├── src/                        # Main application source code
│   ├── agent.py            
│   ├── models/             
│   ├── nodes/              
│   └── utils/              
├── main.py                     # Main CLI entry point
├── requirements.txt            
├── .env.example                
└── README.md                   
```

## Setup Instructions

### 1. Create a Virtual Environment
It is highly recommended to use a virtual environment.
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Variables
Rename the `.env.example` file to `.env` and add your **MeshAPI Key**:
```env
MESHAPI_API_KEY=your_actual_key_here
```
*(The project connects to the MeshAPI endpoint `https://api.meshapi.ai/v1` for LLM inference).*

## Usage

### Building the Vector Database (RAG)
Before running the agent, you can seed the local vector database with existing test cases to ensure the agent doesn't duplicate them.
```powershell
python scripts/rag_ingestion.py
```
This uses local HuggingFace embeddings (`all-MiniLM-L6-v2`) via `sentence-transformers` to index `data/rag_samples/sample_test_cases.csv` into the `chroma_db/` folder.

### Running the Agent
Run the main script and provide the path to your API specification file:
```powershell
python main.py --input data/inputs/sample_swagger.json --output data/outputs/my_test_cases.csv
```

- `--input`: Path to the Swagger (JSON/YAML) or Bruno collection.
- `--output`: (Optional) The name of the output file. Defaults to `generated_test_cases.csv`.

Once complete, review your generated CSV and the associated log file in the `logs/` folder to trace the LLM's decision-making process.
