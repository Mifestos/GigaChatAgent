from gigachat_agent.llm.client import generate_code

task = "Посчитай количество строк в датасете и выведи результат."
schema = "Колонки: customerID, gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, Churn"

print("Отправляем запрос в GigaChat...")
response = generate_code(task, schema)

print("\n--- Сгенерированный код ---")
print(response.code)