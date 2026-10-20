import os
import re
from langchain_gigachat import GigaChat
from pydantic import BaseModel
from gigachat_agent.llm.prompts import get_code_generation_prompt
from dotenv import load_dotenv

load_dotenv()

class LLMResponse(BaseModel):
    code: str
    raw_text: str

# Инициализируем клиента с явным указанием base_url и scope
llm = GigaChat(
    credentials=os.getenv("GIGACHAT_CREDENTIALS"),
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    base_url="https://gigachat.devices.sberbank.ru/api/v1", # Важно для бесплатного тарифа
    verify_ssl_certs=False,
    temperature=0.1
)

def clean_markdown_code(text: str) -> str:
    """Убирает Markdown-обертки ```python ... ```, если нейросеть их добавила."""
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def generate_code(task: str, data_schema: str, previous_error: str = None) -> LLMResponse:
    """Отправляет запрос в GigaChat и возвращает сгенерированный код."""
    prompt = get_code_generation_prompt(task, data_schema, previous_error)
    
    response = llm.invoke(prompt)
    raw_text = response.content
    
    clean_code = clean_markdown_code(raw_text)
    
    return LLMResponse(code=clean_code, raw_text=raw_text)