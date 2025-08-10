"""
API response handling and processing for OpenRouter CLI.
Handles API responses, error handling, and token management.
"""

import time
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from pricing import calculate_session_cost
from utils import format_time_delta

# Initialize Rich console
console = Console()


def process_api_response(response, config, conversation_history, input_tokens, response_tokens, 
                        total_tokens_used, display_max_tokens, message_count, start_time, pricing_info):
    """Process the API response and handle success/error cases"""
    if response.status_code == 200:
        return handle_successful_response(response, conversation_history, input_tokens, 
                                       response_tokens, total_tokens_used, display_max_tokens, 
                                       message_count, start_time, pricing_info)
    else:
        return handle_error_response(response, config, conversation_history)


def handle_successful_response(response, conversation_history, input_tokens, response_tokens,
                             total_tokens_used, display_max_tokens, message_count, start_time, pricing_info):
    """Handle a successful API response"""
    # Calculate response time
    response_time = time.time() - start_time
    formatted_time = format_time_delta(response_time)
    
    # Calculate cost
    exchange_cost = calculate_session_cost(input_tokens, response_tokens, pricing_info)
    
    # Display response information
    console.print(f"[dim]Response time: {formatted_time}[/dim]")
    
    # Enhanced token display with cost
    token_display = f"[dim]Tokens: {input_tokens} (input) + {response_tokens} (response) = {input_tokens + response_tokens} (total)"
    if exchange_cost > 0:
        if exchange_cost < 0.01:
            token_display += f" | Cost: ${exchange_cost:.6f}"
        else:
            token_display += f" | Cost: ${exchange_cost:.4f}"
    token_display += "[/dim]"
    console.print(token_display)
    
    if display_max_tokens:
        console.print(f"[dim]Total Tokens: {total_tokens_used:,} / {display_max_tokens:,}[/dim]")
    
    # Increment message count for successful exchanges
    message_count += 1
    
    return True, response_time


def handle_error_response(response, config, conversation_history):
    """Handle API error responses"""
    try:
        error_data = response.json()
        error_message = error_data.get('error', {}).get('message', str(response.text))
        
        # Special handling for insufficient credits error (402)
        if response.status_code == 402:
            suggestions_text = (
                f"[yellow]Solutions:[/yellow]\n"
                f"• Add credits at: [link=https://openrouter.ai/settings/credits]https://openrouter.ai/settings/credits[/link]\n"
                f"• Browse free models: [cyan]/model[/cyan] → [cyan]2[/cyan] (Show free models only)\n"
                f"• Try the free version if available: [cyan]{config['model']}:free[/cyan]\n"
                f"\n[dim]Original error: {error_message}[/dim]"
            )
            
            console.print(Panel.fit(
                f"[red]Insufficient Credits[/red]\n\n"
                f"The model '[cyan]{config['model']}[/cyan]' requires credits to use.\n\n"
                f"{suggestions_text}",
                title="Payment Required",
                border_style="red"
            ))
        else:
            console.print(f"[red]API Error ({response.status_code}): {error_message}[/red]")
    except Exception:
        console.print(f"[red]API Error: Status code {response.status_code}[/red]")
        console.print(f"[red]{response.text}[/red]")

    # Remove the user's last message since we didn't get a response
    if conversation_history and conversation_history[-1]["role"] == "user":
        conversation_history.pop()
    
    return False, None


def handle_network_error(error, conversation_history):
    """Handle network-related errors"""
    console.print(f"[red]Network error: {str(error)}[/red]")
    # Remove the user's last message since we didn't get a response
    if conversation_history and conversation_history[-1]["role"] == "user":
        conversation_history.pop()


def handle_general_error(error, conversation_history):
    """Handle general errors"""
    console.print(f"[red]Error: {str(error)}[/red]")
    # Remove the user's last message since we didn't get a response
    if conversation_history and conversation_history[-1]["role"] == "user":
        conversation_history.pop()


def handle_keyboard_interrupt():
    """Handle keyboard interrupt gracefully"""
    console.print("\n[yellow]Keyboard interrupt detected. Type /exit to quit.[/yellow]")


def handle_exit():
    """Handle application exit"""
    console.print("\nExiting application...")


def handle_critical_error(error):
    """Handle critical errors during application execution"""
    console.print(f"[red]Critical error: {str(error)}[/red]")
