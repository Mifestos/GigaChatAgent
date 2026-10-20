from pydantic import BaseModel

class BudgetExceeded(Exception):
    """Исключение, которое выбрасывается при превышении лимитов."""
    pass

class BudgetTracker(BaseModel):
    max_iterations: int = 3
    max_tokens: int = 15000
    current_iterations: int = 0
    current_tokens: int = 0

    def check(self):
        """Проверяет, не превышены ли лимиты."""
        if self.current_iterations >= self.max_iterations:
            raise BudgetExceeded(f"Превышен лимит итераций ({self.max_iterations}).")
        if self.current_tokens >= self.max_tokens:
            raise BudgetExceeded(f"Превышен лимит токенов ({self.max_tokens}).")

    def add_iteration(self):
        self.current_iterations += 1

    def add_tokens(self, count: int):
        self.current_tokens += count