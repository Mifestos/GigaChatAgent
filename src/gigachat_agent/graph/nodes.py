from gigachat_agent.graph.state import AgentState
from gigachat_agent.llm.client import generate_code
from gigachat_agent.tools.validator import validate_code
from gigachat_agent.tools.sandbox import run_code_in_sandbox

def generate_code_node(state: AgentState):
    """Узел 1: Просит LLM сгенерировать код."""
    print("\n--- [Шаг 1: Генерация кода] ---")
    
    # Если в состоянии есть ошибка (из прошлой попытки), передаем её в LLM
    previous_error = state.get("error")
    
    response = generate_code(
        task=state["task"],
        data_schema=state["data_schema"],
        previous_error=previous_error
    )
    print(f"Сгенерирован код длиной {len(response.code)} символов.")
    return {"generated_code": response.code, "error": None}

def execute_code_node(state: AgentState):
    """Узел 2: Проверяет код и запускает в песочнице."""
    print("\n--- [Шаг 2: Проверка и выполнение] ---")
    code = state["generated_code"]
    
    # 1. Проверка на безопасность (наш validator)
    validation = validate_code(code)
    if not validation.is_safe:
        error_msg = f"Код не прошел проверку безопасности: {validation.reason}"
        print(error_msg)
        return {"error": error_msg}

    # 2. Выполнение в E2B
    print("Отправляем код в песочницу E2B...")
    # Передаем state.get("data_path") в функцию
    result = run_code_in_sandbox(code, data_path=state.get("data_path"))
    
    if not result.success:
        print(f"Ошибка выполнения: {result.stderr[:100]}...")
        return {"error": result.stderr}
    
    print("Код выполнен успешно!")
    return {"execution_output": result.stdout}