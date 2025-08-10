import os
import time
import configparser
import base64
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Import our security functions
from security import (
    get_or_create_master_key, encrypt_api_key, decrypt_api_key, secure_input_api_key
)

# Import model selection function
from models_selection import select_model

def _format_models_grid(models, columns=2):
    """Format models in a clean horizontal grid layout"""
    grid_lines = []
    
    for i in range(0, len(models), columns):
        row_models = models[i:i+columns]
        
        # Create the model line with consistent spacing
        name_line = ""
        for j, model in enumerate(row_models):
            model_num = i + j + 1
            model_name = model['id'][:30] + "..." if len(model['id']) > 30 else model['id']
            
            if model['id'].endswith(":free"):
                name_line += f"[{model_num:2}] {model_name:<33} [green](FREE)[/green]"
            else:
                name_line += f"[{model_num:2}] {model_name:<40}"
            
            # Add spacing between columns (except for last column)
            if j < len(row_models) - 1:
                name_line += "     "
        
        grid_lines.append(name_line)
        
        # Add empty line between rows for better readability
        if i + columns < len(models):
            grid_lines.append("")
    
    return "\n".join(grid_lines)

def select_model_with_api_key(api_key):
    """Helper function to select model without circular import issues"""
    try:
        import requests
        from rich.console import Console
        from rich.prompt import Prompt
        
        temp_console = Console()
        
        # Fetch models directly using the API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        with temp_console.status("[bold green]Fetching available models..."):
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        
        if response.status_code != 200:
            temp_console.print(f"[red]Error fetching models: {response.status_code}[/red]")
            return None
            
        models_data = response.json()
        all_models = models_data.get("data", [])
        
        if not all_models:
            temp_console.print("[red]No models available. Please check your API key and internet connection.[/red]")
            return None
        
        # Use horizontal card layout for model selection
        from rich.panel import Panel
        temp_console.print(Panel(
            "[bold]Choose Your AI Assistant[/bold]\n\n"
            "[1] All Models            [2] Free Only             [3] Search\n\n"
            "[4] Task Categories       [5] Capabilities          [6] Model Groups\n\n"
            "[q] Cancel selection",
            title="AI Model Selection",
            border_style="cyan",
            padding=(1, 2)
        ))

        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "q"], default="1")

        if choice == "q":
            return None

        elif choice == "3":
            # Direct model name entry
            temp_console.print("[yellow]Enter the exact model name (e.g., 'anthropic/claude-3-opus')[/yellow]")
            model_name = Prompt.ask("Model name")

            # Validate the model name
            model_exists = any(model["id"] == model_name for model in all_models)
            if model_exists:
                return model_name

            temp_console.print("[yellow]Warning: Model not found in available models. Using anyway.[/yellow]")
            confirm = Prompt.ask("Continue with this model name? (y/n)", default="y")
            if confirm.lower() == "y":
                return model_name
            return select_model_with_api_key(api_key)  # Start over

        elif choice == "1":
            # All models in grid layout
            temp_console.print(Panel(
                "[bold]Available Models[/bold]\n\n" + _format_models_grid(all_models),
                title="Model Selection",
                border_style="green",
                padding=(1, 2)
            ))

            model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

            if model_choice.lower() == 'b':
                return select_model_with_api_key(api_key)

            try:
                index = int(model_choice) - 1
                if 0 <= index < len(all_models):
                    selected_model = all_models[index]['id']
                    return selected_model
                else:
                    temp_console.print("[red]Invalid selection[/red]")
                    return select_model_with_api_key(api_key)
            except ValueError:
                temp_console.print("[red]Please enter a valid number[/red]")
                return select_model_with_api_key(api_key)

        elif choice == "2":
            # Show only free models in grid layout
            free_models = [model for model in all_models if model['id'].endswith(":free")]

            if not free_models:
                temp_console.print("[yellow]No free models found.[/yellow]")
                Prompt.ask("Press Enter to continue")
                return select_model_with_api_key(api_key)

            temp_console.print(Panel(
                "[bold]Free Models Available[/bold]\n\n" + _format_models_grid(free_models),
                title="Free Model Selection",
                border_style="green",
                padding=(1, 2)
            ))

            model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

            if model_choice.lower() == 'b':
                return select_model_with_api_key(api_key)

            try:
                index = int(model_choice) - 1
                if 0 <= index < len(free_models):
                    selected_model = free_models[index]['id']
                    return selected_model
                temp_console.print("[red]Invalid selection[/red]")
                Prompt.ask("Press Enter to continue")
                return select_model_with_api_key(api_key)
            except ValueError:
                temp_console.print("[red]Please enter a valid number[/red]")
                Prompt.ask("Press Enter to continue")
                return select_model_with_api_key(api_key)

        elif choice == "4":
            # Browse models by task category
            temp_console.print("[bold green]Task Categories:[/bold green]")
            temp_console.print("[bold]1[/bold] - Creative")
            temp_console.print("[bold]2[/bold] - Coding")
            temp_console.print("[bold]3[/bold] - Analysis")
            temp_console.print("[bold]4[/bold] - Chat")
            temp_console.print("[bold]b[/bold] - Go back")

            task_choice = Prompt.ask("Select task category", choices=["1", "2", "3", "4", "b"], default="1")

            if task_choice == "b":
                return select_model_with_api_key(api_key)

            task_categories = {
                "1": ["claude-3", "gpt-4", "llama", "gemini"],
                "2": ["claude-3-opus", "gpt-4", "deepseek-coder", "qwen-coder", "devstral", "codestral"],
                "3": ["claude-3-opus", "gpt-4", "mistral", "qwen"],
                "4": ["claude-3-haiku", "gpt-3.5", "gemini-pro", "llama"]
            }

            task_patterns = task_categories.get(task_choice, [])
            task_models = []

            for model in all_models:
                model_id = model.get('id', '').lower()
                if any(pattern.lower() in model_id for pattern in task_patterns):
                    task_models.append(model)

            if not task_models:
                temp_console.print("[yellow]No models found for this task category.[/yellow]")
                Prompt.ask("Press Enter to continue")
                return select_model_with_api_key(api_key)

            task_names = {"1": "Creative", "2": "Coding", "3": "Analysis", "4": "Chat"}
            temp_console.print(Panel(
                f"[bold]Models for {task_names.get(task_choice, 'Selected')} Tasks[/bold]\n\n" + _format_models_grid(task_models),
                title="Task Category Models",
                border_style="blue",
                padding=(1, 2)
            ))

            model_choice = Prompt.ask("Enter model number or 'b' to go back", default="1")

            if model_choice.lower() == 'b':
                return select_model_with_api_key(api_key)

            try:
                index = int(model_choice) - 1
                if 0 <= index < len(task_models):
                    selected_model = task_models[index]['id']
                    return selected_model
                else:
                    temp_console.print("[red]Invalid selection[/red]")
                    return select_model_with_api_key(api_key)
            except ValueError:
                temp_console.print("[red]Please enter a valid number[/red]")
                return select_model_with_api_key(api_key)

        else:
            temp_console.print("[yellow]Option not yet implemented. Please choose 1, 2, 3, or 4.[/yellow]")
            return select_model_with_api_key(api_key)
                
    except Exception as e:
        temp_console.print(f"[red]Error during model selection: {str(e)}[/red]")
        return None

# Initialize Rich console
console = Console()

def load_config():
    """Load configuration from .env file and/or config.ini"""
    # First try to load from .env file
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    # Then try config.ini (overrides .env if both exist)
    config = configparser.ConfigParser()
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

    if os.path.exists(config_file):
        config.read(config_file)
        if 'API' in config:
            # Try to load encrypted API key first
            if 'OPENROUTER_API_KEY_ENCRYPTED' in config['API']:
                try:
                    encrypted_key_b64 = config['API']['OPENROUTER_API_KEY_ENCRYPTED']
                    encrypted_key = base64.b64decode(encrypted_key_b64)
                    master_key = get_or_create_master_key()
                    decrypted_key = decrypt_api_key(encrypted_key, master_key)
                    if decrypted_key:
                        api_key = decrypted_key
                    else:
                        console.print("[yellow]Warning: Could not decrypt API key. Please re-enter it.[/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Error decrypting API key: {str(e)}[/yellow]")
            
            # Fallback to plaintext API key
            elif 'OPENROUTER_API_KEY' in config['API'] and config['API']['OPENROUTER_API_KEY']:
                api_key = config['API']['OPENROUTER_API_KEY']

        # Load other settings if available
        if 'SETTINGS' in config:
            settings = config['SETTINGS']
            return {
                'api_key': api_key,
                'model': settings.get('MODEL', ""),
                'temperature': settings.getfloat('TEMPERATURE', 0.7),
                'system_instructions': settings.get('SYSTEM_INSTRUCTIONS', ""),
                'theme': settings.get('THEME', 'default'),
                'max_tokens': settings.getint('MAX_TOKENS', 0),
                'autosave_interval': settings.getint('AUTOSAVE_INTERVAL', 300),
                'streaming': settings.getboolean('STREAMING', True),
                'thinking_mode': settings.getboolean('THINKING_MODE', False)  # Changed default to False
            }

    # Return defaults if no config file
    return {
        'api_key': api_key,
        'model': "",
        'temperature': 0.7,
        'system_instructions': "",
        'theme': 'default',
        'max_tokens': 0,
        'autosave_interval': 300,
        'streaming': True,
        'thinking_mode': False  # Changed default to False
    }

def save_config(config_data):
    """Save configuration to config.ini file with encrypted API key"""
    config = configparser.ConfigParser()
    
    # Handle API key encryption if not in environment
    if 'OPENROUTER_API_KEY' not in os.environ and config_data.get('api_key'):
        try:
            # Encrypt the API key before saving
            master_key = get_or_create_master_key()
            encrypted_key = encrypt_api_key(config_data['api_key'], master_key)
            # Store as base64 for config file compatibility
            encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')
            config['API'] = {'OPENROUTER_API_KEY_ENCRYPTED': encrypted_key_b64}
        except Exception as e:
            console.print(f"[yellow]Warning: Could not encrypt API key: {str(e)}. Saving in plaintext.[/yellow]")
            config['API'] = {'OPENROUTER_API_KEY': config_data['api_key']}
    elif 'OPENROUTER_API_KEY' not in os.environ:
        config['API'] = {'OPENROUTER_API_KEY': config_data['api_key']}
    
    config['SETTINGS'] = {
        'MODEL': config_data['model'],
        'TEMPERATURE': str(config_data['temperature']),
        'SYSTEM_INSTRUCTIONS': config_data['system_instructions'],
        'THEME': config_data['theme'],
        'MAX_TOKENS': str(config_data['max_tokens']),
        'AUTOSAVE_INTERVAL': str(config_data['autosave_interval']),
        'STREAMING': str(config_data['streaming']),
        'THINKING_MODE': str(config_data['thinking_mode'])
    }

    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    
    try:
        with open(config_file, 'w', encoding="utf-8") as f:
            config.write(f)
        
        # Set restrictive permissions on config file (Unix-like systems)
        if os.name != 'nt':  # Not Windows
            os.chmod(config_file, 0o600)
        
        console.print("[green]Configuration saved successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error saving configuration: {str(e)}[/red]")

def setup_wizard():
    """Interactive setup wizard for first-time users"""
    console.print(Panel(
        "[bold blue]Open[/bold blue][bold green]Router[/bold green] [bold cyan]CLI[/bold cyan]\n\n"
        "[bold]Welcome to Your AI Setup![/bold]\n\n"
        "This wizard will guide you through configuring your AI chat experience.\n"
        "We'll set up your API key, choose an AI model, and customize your settings.\n\n"
        "[dim]Estimated time: 2-3 minutes[/dim]\n\n"
        "[bold green]What you'll need:[/bold green]\n"
        "• An OpenRouter API key (get one at [link]https://openrouter.ai[/link])\n"
        "• About 2-3 minutes of your time\n\n"
        "[bold cyan]Ready to get started?[/bold cyan]",
        title="Setup Wizard - Welcome",
        border_style="blue",
        padding=(1, 2)
    ))
    
    # Wait for user to continue
    input("\n[Press Enter to continue...]")
    
    console.print("\n[green]Great! Let's begin the setup process.[/green]\n")

    if "OPENROUTER_API_KEY" not in os.environ:
        console.print(Panel(
            "[bold]Let's connect to OpenRouter[/bold]\n\n"
            "Your API key will be encrypted and stored securely on your device.\n\n"
            "[bold green]Need help getting your API key?[/bold green]\n"
            "1. Go to [link]https://openrouter.ai[/link]\n"
            "2. Sign up or log in to your account\n"
            "3. Navigate to API Keys section\n"
            "4. Create a new API key\n"
            "5. Copy the key and paste it below",
            title="API Key Setup",
            border_style="yellow",
            padding=(1, 2)
        ))
        
        # Loop until we get a valid API key or user explicitly cancels
        while True:
            api_key = secure_input_api_key()
            if not api_key:
                console.print("[red]Invalid API key provided.[/red]")
                retry = Prompt.ask("Would you like to try again? (y/n)", default="y")
                if retry.lower() != 'y':
                    console.print("[red]Setup cancelled - no valid API key provided[/red]")
                    return None
                continue  # Ask for API key again
            else:
                break  # Valid API key received, exit loop
    else:
        api_key = os.getenv("OPENROUTER_API_KEY")

    # Save API key temporarily to allow model fetching
    temp_config = {'api_key': api_key, 'thinking_mode': False}  # Default to disabled

    # Use the simplified model selection
    console.print(Panel(
        "[bold]Choose Your AI Assistant[/bold]\n\n"
        "Select the AI model that will power your conversations.\n"
        "You can change this later using the /model command.",
        title="AI Model Selection",
        border_style="cyan",
        padding=(1, 2)
    ))
    model = ""
    thinking_mode = False  # Default value - disabled
    try:
        with console.status("[bold green]Connecting to OpenRouter...[/bold green]"):
            # Small delay to ensure the API key is registered
            time.sleep(1)

        # Call the select_model function to get user's choice
        # Pass the API key directly to avoid circular import issues
        selected_model = select_model_with_api_key(api_key)
        if selected_model:
            model = selected_model
            # Use the thinking_mode value that was set during model selection
            thinking_mode = temp_config.get('thinking_mode', False)
        else:
            console.print("[yellow]Model selection cancelled. You can set a model later.[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Error during model selection: {str(e)}. You can set a model later.[/yellow]")

    console.print(Panel(
        "[bold]Temperature: Controls response creativity[/bold]\n\n"
        "[dim][0.0 = Focused and consistent] [2.0 = Creative and varied][/dim]\n\n"
        "Recommended values:\n"
        "• 0.1-0.3: Factual, precise responses\n"
        "• 0.5-0.7: Balanced creativity and consistency\n"
        "• 0.8-1.0: More creative and varied responses\n"
        "• 1.0+: Highly creative but potentially unpredictable",
        title="Chat Settings",
        border_style="magenta",
        padding=(1, 2)
    ))
    
    temperature = float(Prompt.ask("Set temperature (0.0-2.0)", default="0.7"))
    if temperature > 1.0:
        console.print("[yellow]Warning: High temperature values (>1.0) may cause erratic or nonsensical responses.[/yellow]")
        confirm = Prompt.ask("Are you sure you want to use this high temperature? (y/n)", default="n")
        if confirm.lower() != 'y':
            temperature = float(Prompt.ask("Enter a new temperature value (0.0-1.0)", default="0.7"))

    console.print(Panel(
        "[bold]Guide the AI's behavior and personality[/bold]\n\n"
        "[bold green]Examples:[/bold green]\n"
        "• \"You are a helpful coding assistant\"\n"
        "• \"You are a creative writing partner\"\n"
        "• \"You are a professional business consultant\"\n"
        "• \"You are an expert in data analysis\"\n\n"
        "[dim]Press Enter twice to finish, or just press Enter for default[/dim]",
        title="System Instructions",
        border_style="yellow",
        padding=(1, 2)
    ))
    
    lines = []
    empty_line_count = 0
    while True:
        line = input()
        if not line:
            empty_line_count += 1
            if empty_line_count >= 2:  # Exit after two consecutive empty lines
                break
        else:
            empty_line_count = 0  # Reset counter if non-empty line
            lines.append(line)

    # If no instructions provided, use a default value
    if not lines:
        system_instructions = "You are a helpful AI assistant."
        console.print("[yellow]No system instructions provided. Using default instructions.[/yellow]")
    else:
        system_instructions = "\n".join(lines)

    # Add theme selection
    available_themes = ['default', 'dark', 'light', 'hacker']
    console.print(Panel(
        "[bold]Choose your visual appearance[/bold]\n\n"
        "[1] default\n"
        "[2] dark\n"
        "[3] light\n"
        "[4] hacker",
        title="Theme Selection",
        border_style="cyan",
        padding=(1, 2)
    ))
    theme_choice = Prompt.ask("Select theme", choices=available_themes, default="default")

    # We already asked about thinking mode during model selection, so we'll use that value
    # Only ask if model selection failed or was cancelled
    if not model:
        # Enhanced thinking mode explanation
        console.print(Panel.fit(
            "[yellow]Thinking Mode:[/yellow]\n\n"
            "Thinking mode shows the AI's reasoning process between <thinking> and </thinking> tags.\n"
            "This reveals how the AI approaches your questions and can help you understand its thought process.\n\n"
            "[dim]Note: Not all models support this feature. If you notice issues with responses, you can disable it later with /thinking-mode[/dim]",
            title="AI Reasoning Process",
            border_style="yellow"
        ))

        thinking_mode = Prompt.ask(
            "Enable thinking mode?",
            choices=["y", "n"],
            default="n"
        ).lower() == "y"

    config_data = {
        'api_key': api_key,
        'model': model,
        'temperature': temperature,
        'system_instructions': system_instructions,
        'theme': theme_choice,
        'max_tokens': 0,
        'autosave_interval': 300,
        'streaming': True,
        'thinking_mode': thinking_mode
    }

    save_config(config_data)
    
    # Show completion summary
    console.print(Panel(
        "[bold]Your OpenRouter CLI is ready to use![/bold]\n\n"
        "[bold green]Configuration Summary:[/bold green]\n"
        f"• API Key: [green]Configured[/green]\n"
        f"• Model: [cyan]{model or 'Not selected'}[/cyan]\n"
        f"• Temperature: [yellow]{temperature}[/yellow]\n"
        f"• Theme: [magenta]{theme_choice}[/magenta]\n"
        f"• Thinking Mode: [blue]{'Enabled' if thinking_mode else 'Disabled'}[/blue]\n\n"
        "[bold cyan]Starting your AI chat experience...[/bold cyan]",
        title="Setup Complete!",
        border_style="green",
        padding=(1, 2)
    ))
    
    input("\n[Press Enter to continue...]")
    return config_data
