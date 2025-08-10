"""
Model recommendation functions for OpenRouter CLI.
Provides intelligent model suggestions based on task type and budget constraints.
"""

from rich.console import Console
from models_core import get_available_models
from models_filtering import get_dynamic_task_categories

# Initialize Rich console
console = Console()


def get_model_recommendations(task_type=None, budget=None):
    """Recommends models based on task type and budget constraints using dynamic OpenRouter categories"""
    all_models = get_available_models()

    if not task_type:
        return all_models

    # Get dynamic task categories from OpenRouter API instead of hardcoded ones
    try:
        task_categories = get_dynamic_task_categories()
        console.print(f"[dim]Using dynamic categories for task: {task_type}[/dim]")
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to get dynamic categories, using fallback patterns: {str(e)}[/yellow]")
        # Fallback to basic patterns if API fails
        task_categories = {
            "creative": ["claude-3", "gpt-4", "llama", "gemini"],
            "coding": ["claude-3-opus", "gpt-4", "deepseek-coder", "qwen-coder", "devstral", "codestral"],
            "analysis": ["claude-3-opus", "gpt-4", "mistral", "qwen"],
            "chat": ["claude-3-haiku", "gpt-3.5", "gemini-pro", "llama"]
        }

    recommended = []
    task_model_patterns = task_categories.get(task_type, [])
    
    for model in all_models:
        model_id = model.get('id', '').lower()
        # Check if model matches any of the task-specific patterns/slugs
        if any(pattern.lower() in model_id for pattern in task_model_patterns):
            # Filter by budget if specified
            if budget == "free" and ":free" in model['id']:
                recommended.append(model)
            elif budget is None or budget != "free":
                recommended.append(model)

    return recommended or all_models
