from typing import TypedDict, List, Dict, Any

class Scenario(TypedDict):
    name: str
    description: str
    type: str # positive, negative, edge_case

class TestCase(TypedDict):
    name: str
    scenario_type: str
    description: str
    steps: List[str]
    expected_result: str

class AgentState(TypedDict):
    file_path: str
    api_spec: Dict[str, Any] # The parsed API spec
    scenarios: List[Scenario]
    test_cases: List[TestCase]
    final_csv: str
    errors: List[str]
