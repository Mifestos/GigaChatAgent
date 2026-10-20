from gigachat_agent.graph.state import AgentState
from gigachat_agent.llm.client import generate_code
from gigachat_agent.tools.validator import validate_code
from gigachat_agent.tools.sandbox import run_code_in_sandbox
from gigachat_agent.guardrails.budget import BudgetExceeded

def generate_code_node(state: AgentState):
    """Узел 1: Просит LLM сгенерировать код с учетом бюджета."""
    print("\n--- [Шаг 1: Генерация кода] ---")
    
    budget = state["budget"]
    
    # 1. Проверяем, не вышли ли за лимиты (бросает BudgetExceeded, если да)
    budget.check()
    
    # 2. Увеличиваем счетчик итераций
    budget.add_iteration()
    
    # 3. Получаем ошибку из прошлой попытки (для self-correction)
    previous_error = state.get("error")
    
    # 4. Запрашиваем код у GigaChat
    response = generate_code(
        task=state["task"],
        data_schema=state["data_schema"],
        previous_error=previous_error
    )
    
    # 5. Увеличиваем счетчик токенов
    budget.add_tokens(response.tokens_used)
    
    print(f"Сгенерирован код ({len(response.code)} символов). Потрачено токенов: ~{response.tokens_used}. Всего: {budget.current_tokens}")
    
    # 6. Возвращаем обновленное состояние (не забываем вернуть budget!)
    return {"generated_code": response.code, "error": None, "budget": budget}

def execute_code_node(state: AgentState):
    """Узел 2: Проверяет код и запускает в песочнице."""
    print("\n--- [Шаг 2: Проверка и выполнение] ---")
    code = state["generated_code"]
    
    # 1. Проверка на безопасность
    validation = validate_code(code)
    if not validation.is_safe:
        error_msg = f"Код не прошел проверку безопасности: {validation.reason}"
        print(error_msg)
        return {"error": error_msg}

    # 2. Выполнение в E2B
    print("Отправляем код в песочницу E2B...")
    result = run_code_in_sandbox(code, data_path=state.get("data_path"))
    
    if not result.success:
        print(f"Ошибка выполнения: {result.stderr[:100]}...")
        return {"error": result.stderr}
    
    print("Код выполнен успешно!")
    return {"execution_output": result.stdout}