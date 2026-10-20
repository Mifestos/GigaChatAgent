from gigachat_agent.graph.builder import app

# Начальное состояние
initial_state = {
    "task": "Напиши код, который выводит числа от 1 до 5 с помощью цикла.",
    "data_schema": "Данные не требуются.",
    "data_path": None,  
    "generated_code": None,
    "execution_output": None,
    "error": None
}

print("Запускаем агента...")
# Запускаем граф. recursion_limit=3 означает: максимум 5 попыток (1 начальная + 4 исправления)
final_state = app.invoke(initial_state, config={"recursion_limit": 5})

print("\n" + "="*30)
print("=== ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ===")
if final_state.get("error"):
    print("Агент не смог решить задачу. Последняя ошибка:")
    print(final_state["error"])
else:
    print("Успешно выполнено! Вывод из песочницы:")
    print(final_state["execution_output"])