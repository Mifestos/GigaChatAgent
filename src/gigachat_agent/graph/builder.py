from langgraph.graph import StateGraph, END
from gigachat_agent.graph.state import AgentState
from gigachat_agent.graph.nodes import generate_code_node, execute_code_node
from gigachat_agent.guardrails.budget import BudgetExceeded

def should_continue(state: AgentState):
    if state.get("error"):
        return "generate"
    return END

# Создаем граф
workflow = StateGraph(AgentState)

# Добавляем узлы (наши шаги)
workflow.add_node("generate", generate_code_node)
workflow.add_node("execute", execute_code_node)

# Устанавливаем точку входа (с чего начинаем)
workflow.set_entry_point("generate")

# Добавляем прямую связь: после генерации всегда идем на выполнение
workflow.add_edge("generate", "execute")

# Добавляем условный переход (если ошибка - назад к генерации, иначе - конец)
workflow.add_conditional_edges(
    "execute",
    should_continue,
    {
        "generate": "generate",
        END: END
    }
)

# Компилируем граф в готовое приложение
app = workflow.compile()