from typing import TypedDict, Optional

class AgentState(TypedDict):
    task: str
    data_schema: str
    data_path: Optional[str]  
    generated_code: Optional[str]
    execution_output: Optional[str]
    error: Optional[str]