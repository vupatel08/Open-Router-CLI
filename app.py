"""
Main application logic for OpenRouter CLI.
Handles argument parsing, setup, and application initialization.
"""

import os
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from config import load_config, save_config, setup_wizard
from ui import create_chat_ui
from models_selection import select_model
from recommendations import get_model_recommendations
from files import handle_attachment

# Initialize Rich console
console = Console()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="OpenRouter CLI - AI chat powered by OpenRouter")
    parser.add_argument("--setup", action="store_true", help="Run the setup wizard")
    parser.add_argument("--model", type=str, help="Specify model to use")
    parser.add_argument("--task", type=str, choices=["creative", "coding", "analysis", "chat"],
                        help="Optimize for specific task type")
    parser.add_argument("--image", type=str, help="Path to image file to analyze")
    return parser.parse_args()


def check_config_exists():
    """Check if configuration files exist"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    return config_file, env_file


def handle_setup_or_config(args, config_file, env_file):
    """Handle setup wizard or load existing configuration"""
    if args.setup or (not os.path.exists(config_file) and not os.path.exists(env_file)):
        config = setup_wizard()
        if config is None:
            console.print("[red]Setup failed. Cannot continue without proper configuration. Exiting.[/red]")
            sys.exit(1)
        return config
    else:
        return load_config()


def validate_api_key(config):
    """Validate that API key is properly set"""
    if not config['api_key'] or config['api_key'] == "<YOUR_OPENROUTER_API_KEY>":
        console.print("[red]API key not found or not set correctly.[/red]")
        setup_choice = Prompt.ask("Would you like to run the setup wizard? (y/n)", default="y")
        if setup_choice.lower() == 'y':
            config = setup_wizard()
            if config is None:
                console.print("[red]Setup failed. Cannot continue without a valid API key. Exiting.[/red]")
                sys.exit(1)
        else:
            console.print("[red]Cannot continue without a valid API key. Exiting.[/red]")
            sys.exit(1)
    return config


def handle_task_recommendations(args, config):
    """Handle task-specific model recommendations"""
    if args.task:
        recommended_models = get_model_recommendations(args.task)
        if recommended_models:
            console.print(Panel.fit(
                f"[bold green]Recommended models for {args.task} tasks:[/bold green]\n" +
                "\n".join([f"- {model['id']}" for model in recommended_models[:5]]),
                title="Task Optimization"
            ))

            use_recommended = Prompt.ask(
                "Would you like to use one of these recommended models?",
                choices=["y", "n"],
                default="y"
            )

            if use_recommended.lower() == 'y':
                # Let user select from recommended models
                for i, model in enumerate(recommended_models[:5], 1):
                    console.print(f"[bold]{i}.[/bold] {model['id']}")

                choice = Prompt.ask("Select model number", default="1")
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(recommended_models[:5]):
                        config['model'] = recommended_models[index]['id']
                        save_config(config)
                except ValueError:
                    pass


def handle_model_selection(args, config):
    """Handle model selection and validation"""
    if args.model:
        config['model'] = args.model
        save_config(config)
    elif not config['model']:
        console.print("[yellow]No model selected. Please choose a model.[/yellow]")
        selected_model = select_model(config)
        if selected_model:
            config['model'] = selected_model
            save_config(config)
        else:
            console.print("[red]Cannot continue without a valid model. Exiting.[/red]")
            sys.exit(1)


def ensure_system_instructions(config):
    """Ensure system instructions are set"""
    if not config['system_instructions']:
        # Only prompt for system instructions if they weren't already set during setup
        # Set a default value without prompting
        config['system_instructions'] = "You are a helpful AI assistant."
        console.print("[yellow]No system instructions set. Using default instructions.[/yellow]")
        save_config(config)


def handle_image_analysis(args, config):
    """Handle image analysis if provided via command line"""
    conversation_history = []
    if args.image:
        conversation_history = [
            {"role": "system", "content": config['system_instructions']}
        ]
        success, message = handle_attachment(args.image, conversation_history)
        if success:
            console.print(f"[green]{message}[/green]")
        else:
            console.print(f"[red]{message}[/red]")
    return conversation_history


def initialize_application():
    """Initialize the OpenRouter CLI application"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Check configuration
    config_file, env_file = check_config_exists()
    config = handle_setup_or_config(args, config_file, env_file)
    
    # Show welcome UI
    create_chat_ui()
    
    # Validate API key
    config = validate_api_key(config)
    
    # Handle task-specific recommendations
    handle_task_recommendations(args, config)
    
    # Handle model selection
    handle_model_selection(args, config)
    
    # Ensure system instructions are set
    ensure_system_instructions(config)
    
    # Handle image analysis if provided
    conversation_history = handle_image_analysis(args, config)
    
    return config, conversation_history
