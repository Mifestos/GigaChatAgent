import json
from typing import List, Dict
from gigachat_agent.graph.builder import app
from gigachat_agent.guardrails.budget import BudgetTracker
from rich.console import Console
from rich.table import Table

console = Console()

def load_golden_tasks(filepath: str = "data/golden_tasks.json") -> List[Dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation():
    tasks = load_golden_tasks()
    results = []
    
    console.print(f"[bold cyan]Запускаем оценку на {len(tasks)} задачах...[/bold cyan]\n")
    
    for i, item in enumerate(tasks, 1):
        console.print(f"[bold]Задача {i}/{len(tasks)}:[/bold] {item['task']}")
        
        initial_state = {
            "task": item["task"],
            "data_schema": "Колонки: customerID, gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, ..., MonthlyCharges, TotalCharges, Churn.",
            "data_path": "data/raw/data.csv",
            "generated_code": None,
            "execution_output": None,
            "error": None,
            "budget": BudgetTracker(max_iterations=3, max_tokens=15000)
        }
        
        try:
            # Запускаем граф
            final_state = app.invoke(initial_state, config={"recursion_limit": 10})
            
            output = final_state.get("execution_output", "")
            error = final_state.get("error")
            
            # Проверка: нет ошибки И ожидаемая строка есть в выводе
            is_correct = not error and (item["expected_output_contains"] in output)
            
            results.append({
                "id": item["id"],
                "task": item["task"],
                "passed": is_correct,
                "output": output.strip(),
                "error": error
            })
            
            if is_correct:
                console.print("  ✅ [green]PASSED[/green]")
            else:
                console.print(f"  ❌ [red]FAILED[/red]. Ожидалось '{item['expected_output_contains']}', получено: {output[:50]}...")
                
        except Exception as e:
            console.print(f"  ❌ [red]ERROR[/red]: {str(e)}")
            results.append({
                "id": item["id"],
                "task": item["task"],
                "passed": False,
                "output": "",
                "error": str(e)
            })
            
    # Считаем метрики
    passed_count = sum(1 for r in results if r["passed"])
    pass_at_1 = (passed_count / len(results)) * 100
    
    console.print("\n" + "="*40)
    console.print("[bold yellow]=== ИТОГОВЫЙ ОТЧЕТ ===[/bold yellow]")
    
    table = Table(title="Результаты Evaluation")
    table.add_column("ID", style="cyan")
    table.add_column("Статус", justify="center")
    table.add_column("Задача", style="white")
    
    for r in results:
        status = "[green]PASSED[/green]" if r["passed"] else "[red]FAILED[/red]"
        table.add_row(r["id"], status, r["task"])
        
    console.print(table)
    
    console.print(f"\n[bold green]Pass@1 (Точность с первого раза): {pass_at_1:.1f}% ({passed_count}/{len(results)})[/bold green]")
    
    return results, pass_at_1

if __name__ == "__main__":
    run_evaluation()