import typer
import os
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from gigachat_agent.graph.builder import app
from langgraph.errors import GraphRecursionError
from gigachat_agent.guardrails.budget import BudgetTracker, BudgetExceeded

cli = typer.Typer(help="GigaChatAgent: AI-ассистент для анализа данных.")
console = Console()

@cli.command()
def analyze(
    file: str = typer.Option(..., "--file", "-f", help="Путь к CSV-файлу с данными"),
    query: str = typer.Option(..., "--query", "-q", help="Текстовая задача для агента"),
):
    """Запускает AI-агента для анализа указанного файла."""
    
    if not os.path.exists(file):
        console.print(f"[bold red]Ошибка:[/bold red] Файл {file} не найден.")
        raise typer.Exit(1)

    # Читаем только заголовки и пару строк для схемы (экономим память)
    try:
        df = pd.read_csv(file, nrows=3)
        columns = ", ".join(df.columns.tolist())
        schema = f"Колонки в файле: {columns}. Пример данных:\n{df.head(2).to_string()}"
    except Exception as e:
        console.print(f"[bold yellow]Предупреждение:[/bold yellow] Не удалось прочитать схему CSV. {e}")
        schema = "Схема неизвестна."

    console.print(Panel.fit(
        f"[bold green]Задача:[/bold green] {query}\n"
        f"[bold blue]Файл:[/bold blue] {file}",
        title="GigaChatAgent",
        border_style="green"
    ))

    # ВАЖНО: Инициализируем бюджет и передаем его в граф!
    initial_state = {
        "task": query,
        "data_schema": schema,
        "data_path": file,
        "generated_code": None,
        "execution_output": None,
        "error": None,
        "budget": BudgetTracker(max_iterations=3, max_tokens=15000) # <-- Добавили бюджет
    }

    # Запускаем агента
    try:
        with console.status("[bold yellow]Агент думает и пишет код...[/bold yellow]"):
            # Увеличили recursion_limit для LangGraph, чтобы сработал наш BudgetTracker
            final_state = app.invoke(initial_state, config={"recursion_limit": 10})
            
    except BudgetExceeded as e:
        console.print(Panel(
            f"[bold red]Бюджет исчерпан![/bold red]\n\n{str(e)}\n"
            "Агент остановлен, чтобы не тратить лишние ресурсы.",
            title="Остановка по лимитам",
            border_style="red"
        ))
        raise typer.Exit(1)
        
    except GraphRecursionError:
        console.print(Panel(
            "[bold red]Превышен лимит попыток исправления![/bold red]\n\n"
            "Агент слишком много раз пытался написать код, но он падал с ошибкой.",
            title="Ошибка агента",
            border_style="red"
        ))
        raise typer.Exit(1)

    console.print("\n[bold]=== Результат ===[/bold]")
    
    if final_state.get("error"):
        console.print(Panel(
            f"[bold red]Агент не смог решить задачу.[/bold red]\n\n{final_state['error']}",
            title="Ошибка",
            border_style="red"
        ))
    else:
        console.print("[bold cyan]Сгенерированный код:[/bold cyan]")
        syntax = Syntax(final_state["generated_code"], "python", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        console.print("\n[bold green]Вывод выполнения:[/bold green]")
        console.print(Panel(final_state["execution_output"], border_style="green"))

if __name__ == "__main__":
    cli()