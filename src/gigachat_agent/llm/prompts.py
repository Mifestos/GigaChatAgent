def get_code_generation_prompt(task: str, data_schema: str, previous_error: str = None) -> str:
    """
    Формирует промпт для GigaChat, чтобы тот написал код.
    """
    prompt = f"""Ты — экспертный Python-разработчик и дата-сайентист.
Твоя задача — написать код для анализа данных на основе задачи пользователя.

ЗАДАЧА: {task}

ИНФОРМАЦИЯ О ДАННЫХ (CSV файл лежит в текущей директории как 'data.csv'):
{data_schema}

ПРАВИЛА:
1. Верни ТОЛЬКО валидный Python-код.
2. Не используй сетевые запросы (requests, urllib) и системные команды (os.system).
3. Для загрузки данных используй: import pandas as pd; df = pd.read_csv('data.csv')
4. Обязательно выводи результат через print(), чтобы я мог его прочитать.
5. Не оборачивай код в Markdown-разметку (без ```python ... ```).
"""

    if previous_error:
        prompt += f"""
ВНИМАНИЕ: Твой предыдущий код упал с ошибкой. Исправь её!
ТЕКСТ ОШИБКИ:
{previous_error}
"""

    return prompt