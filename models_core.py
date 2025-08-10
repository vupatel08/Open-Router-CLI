import requests
from rich.console import Console

# Initialize Rich console
console = Console()

def get_available_models():
    """Fetch available models from OpenRouter API"""
    try:
        # Import here to avoid circular imports
        from config import load_config
        
        config = load_config()
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        with console.status("[bold green]Fetching available models..."):
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)

        if response.status_code == 200:
            models_data = response.json()
            return models_data["data"]
        console.print(f"[red]Error fetching models: {response.status_code}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]Error fetching models: {str(e)}[/red]")
        return []

def get_model_info(model_id):
    """Get model information of all models"""
    models = get_available_models()
    
    try:
        for model in models:
            if model["id"] == model_id:
                return model
        
        console.print(f"[yellow]Warning: Could not find info for model '{model_id}'.[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red] Failed to fetch model info: {str(e)}[/red]")
        return None

def get_enhanced_models():
    """Fetch enhanced model data from OpenRouter frontend API with detailed capabilities"""
    try:
        # Import here to avoid circular imports
        from config import load_config
        
        config = load_config()
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        with console.status("[bold green]Fetching enhanced model data..."):
            response = requests.get("https://openrouter.ai/api/frontend/models", headers=headers)

        if response.status_code == 200:
            models_data = response.json()
            return models_data.get("data", [])
        else:
            console.print(f"[red]Error fetching enhanced models: {response.status_code}[/red]")
            # Fallback to standard models API
            return get_available_models()
    except Exception as e:
        console.print(f"[red]Error fetching enhanced models: {str(e)}[/red]")
        # Fallback to standard models API
        return get_available_models()
