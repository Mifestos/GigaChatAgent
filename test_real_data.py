from gigachat_agent.graph.builder import app

# Начальное состояние с указанием пути к реальному файлу
initial_state = {
    "task": "Прочитай датасет, выведи количество строк и столбцов, а также посчитай, сколько клиентов ушло (колонка Churn).",
    "data_schema": "Колонки: customerID, gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, MultipleLines, InternetService, ..., Churn (Yes/No).",
    "data_path": "data/raw/data.csv", 
    "generated_code": None,
    "execution_output": None,
    "error": None
}

print("Запускаем агента на реальных данных...")
final_state = app.invoke(initial_state, config={"recursion_limit": 5})

print("\n" + "="*30)
print("=== ФИНАЛЬНЫЙ РЕЗУЛЬТАТ ===")
if final_state.get("error"):
    print("Агент не смог решить задачу. Последняя ошибка:")
    print(final_state["error"])
else:
    print("Успешно выполнено! Вывод из песочницы:")
    print(final_state["execution_output"])