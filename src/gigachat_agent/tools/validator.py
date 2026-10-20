import re
import ast
from typing import Literal
from pydantic import BaseModel

class ValidationResult(BaseModel):
    is_safe: bool
    reason: str = ""
    risk_level: Literal["low", "medium", "high"] = "low"

# Запрещенные паттерны
FORBIDDEN_PATTERNS = [
    (r"os\.system", "Вызов системных команд (os.system)"),
    (r"subprocess", "Запуск подпроцессов (subprocess)"),
    (r"pip install", "Установка пакетов (pip install)"),
    (r"requests", "Сетевые запросы (requests)"),
    (r"urllib", "Сетевые запросы (urllib)"),
    (r"socket", "Сетевые сокеты (socket)"),
    (r"eval\(", "Использование eval (небезопасно)"),
    (r"exec\(", "Использование exec (небезопасно)"),
    (r"__import__", "Динамический импорт (__import__)"),
]

def validate_code(code: str) -> ValidationResult:
    """Проверяет код на опасные конструкции."""
    for pattern, description in FORBIDDEN_PATTERNS:
        if re.search(pattern, code):
            return ValidationResult(
                is_safe=False,
                reason=f"Найдено запрещенное действие: {description}",
                risk_level="high"
            )

    try:
        ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(
            is_safe=False,
            reason=f"Синтаксическая ошибка: {e}",
            risk_level="medium"
        )

    return ValidationResult(is_safe=True)