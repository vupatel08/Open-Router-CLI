"""
Session management functions for OpenRouter CLI.
Handles session initialization, tracking, and management.
"""

import os
import time
import datetime
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit.history import InMemoryHistory

from app_info import APP_VERSION
from pricing import get_model_pricing_info
from models_core import get_model_info
from files import manage_context_window

# Initialize Rich console
console = Console()

# Check if prompt_toolkit is available
try:
    from prompt_toolkit.history import InMemoryHistory
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


def initialize_session(config, conversation_history=None):
    """Initialize a new chat session with all necessary setup"""
    if conversation_history is None:
        # Use user's thinking mode preference instead of model detection
        if config['thinking_mode']:
            # Make the thinking instruction more explicit and mandatory
            thinking_instruction = (
                f"{config['system_instructions']}\n\n"
                "CRITICAL INSTRUCTION: For EVERY response without exception, you MUST first explain your "
                "thinking process between <thinking> and </thinking> tags, even for simple greetings or short "
                "responses. This thinking section should explain your reasoning and approach. "
                "After the thinking section, provide your final response. Example format:\n"
                "<thinking>Here I analyze what to say, considering context and appropriate responses...</thinking>\n"
                "This is my actual response to the user."
            )
        else:
            # Use standard instructions without thinking tags
            thinking_instruction = config['system_instructions']

        conversation_history = [
            {"role": "system", "content": thinking_instruction}
        ]

    # Initialize command history for session
    if HAS_PROMPT_TOOLKIT:
        session_history = InMemoryHistory()
    else:
        session_history = None

    # Check if temperature is too high and warn the user
    if config['temperature'] > 1.0:
        console.print(Panel.fit(
            f"[yellow]Warning: High temperature setting ({config['temperature']}) may cause erratic responses.[/yellow]\n"
            f"Consider using a value between 0.0 and 1.0 for more coherent outputs.",
            title="High Temperature Warning",
            border_style="yellow"
        ))

    # Get pricing information for the model
    pricing_info = get_model_pricing_info(config['model'])
    pricing_display = f"[cyan]Pricing:[/cyan] {pricing_info['display']}"
    if pricing_info['is_free']:
        pricing_display += f" [green]({pricing_info['provider']})[/green]"
    else:
        pricing_display += f" [dim]({pricing_info['provider']})[/dim]"

    console.print(Panel(
        f"[bold blue]Open[/bold blue][bold green]Router[/bold green] [bold cyan]CLI[/bold cyan] [dim]v{APP_VERSION}[/dim]\n"
        f"[cyan]Model:[/cyan] {config['model']}\n"
        f"[cyan]Temperature:[/cyan] {config['temperature']}\n"
        f"[cyan]Thinking mode:[/cyan] {'[green]✓ Enabled[/green]' if config['thinking_mode'] else '[yellow]✗ Disabled[/yellow]'}\n"
        f"{pricing_display}\n"
        f"[cyan]Session started:[/cyan] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Type your message or use commands: /help for available commands",
        title="Chat Session Active",
        border_style="green",
        padding=(1, 2)
    ))

    # Add session tracking
    session_start_time = time.time()
    total_tokens_used = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    response_times = []
    message_count = 0
    max_tokens = config.get('max_tokens')
    
    if not max_tokens or max_tokens == 0:
        model_info = get_model_info(config['model'])
        if model_info and 'context_length' in model_info and model_info['context_length']:
            max_tokens = model_info['context_length']
            console.print(f"[dim]Using model's context length: {max_tokens:,} tokens[/dim]")
        else:
            max_tokens = 8192
            console.print(f"[yellow]Could not determine model's context length. Using default: {max_tokens:,} tokens[/yellow]")
    else:
        console.print(f"[dim]Using user-defined max tokens: {max_tokens:,}[/dim]")

    # Create a session directory for saving files
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions", session_id)
    os.makedirs(session_dir, exist_ok=True)

    # Auto-save conversation periodically
    last_autosave = time.time()
    autosave_interval = config['autosave_interval']

    # Check if we need to trim the conversation history
    conversation_history, trimmed_count = manage_context_window(conversation_history, max_tokens=max_tokens, model_name=config['model'])
    if trimmed_count > 0:
        console.print(f"[yellow]Note: Removed {trimmed_count} earlier messages to stay within the context window.[/yellow]")

    return {
        'conversation_history': conversation_history,
        'session_history': session_history,
        'session_start_time': session_start_time,
        'total_tokens_used': total_tokens_used,
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'response_times': response_times,
        'message_count': message_count,
        'max_tokens': max_tokens,
        'session_dir': session_dir,
        'last_autosave': last_autosave,
        'autosave_interval': autosave_interval,
        'pricing_info': pricing_info
    }


def get_session_headers(config):
    """Get the headers for API requests"""
    return {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
