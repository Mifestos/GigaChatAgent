from typing import TypedDict, Optional
from gigachat_agent.guardrails.budget import BudgetTracker

class AgentState(TypedDict):
    task: str
    data_schema: str
    data_path: Optional[str]
    generated_code: Optional[str]
    execution_output: Optional[str]
    error: Optional[str]
    budget: BudgetTracker  