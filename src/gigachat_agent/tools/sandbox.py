import os
from e2b_code_interpreter import Sandbox
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class ExecutionResult(BaseModel):
    success: bool
    stdout: str = ""
    stderr: str = ""

def run_code_in_sandbox(code: str, data_path: str = None, timeout_sec: int = 30) -> ExecutionResult:
    """Выполняет код в изолированной песочнице E2B."""
    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        return ExecutionResult(success=False, stderr="E2B_API_KEY не найден в .env")

    sandbox = None
    try:
        sandbox = Sandbox.create(template="code-interpreter-v1", api_key=api_key)
        
        # Если передан путь к файлу, загружаем его в песочницу
        if data_path and os.path.exists(data_path):
            with open(data_path, "rb") as f:
                # E2B сохранит файл под именем 'data.csv' в корне песочницы
                sandbox.files.write("data.csv", f.read())

                # Выполняем код
        execution = sandbox.run_code(code)
        
        # Надёжный сбор stdout: E2B может вернуть строку или список строк
        raw_stdout = execution.logs.stdout
        if isinstance(raw_stdout, list):
            # Если это список строк, просто соединяем их
            stdout_text = "".join(raw_stdout)
        else:
            # Если это уже строка (или None), приводим к строке
            stdout_text = str(raw_stdout) if raw_stdout else ""
              
        if execution.error:
            stderr_text = f"{execution.error.name}: {execution.error.value}\n{execution.error.traceback}"
            return ExecutionResult(success=False, stdout=stdout_text, stderr=stderr_text)
            
        return ExecutionResult(success=True, stdout=stdout_text)
        
    except Exception as e:
        return ExecutionResult(success=False, stderr=f"Ошибка песочницы: {str(e)}")
    finally:
        if sandbox:
            sandbox.kill()