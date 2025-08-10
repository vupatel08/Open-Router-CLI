"""
Chat functionality for OpenRouter CLI.
Handles the main chat loop and model interaction.
"""

import time
import requests
from rich.console import Console
from rich.panel import Panel

from session import initialize_session, get_session_headers
from commands import (
    handle_help_command, handle_clear_command, handle_new_command, handle_save_command,
    handle_settings_command, handle_tokens_command, handle_speed_command, handle_model_command,
    handle_temperature_command, handle_system_command, handle_theme_command, handle_attach_command,
    handle_thinking_command, handle_thinking_mode_command, handle_clear_screen_command
)
from api_handler import process_api_response
from models_core import get_model_info
from files import manage_context_window
from utils import count_tokens
from ui import HAS_PROMPT_TOOLKIT, get_user_input_with_completion
from conversation import stream_response
from app_info import show_about, check_for_updates

# Initialize Rich console
console = Console()


def chat_with_model(config, conversation_history=None):
    """Main chat loop with the selected model"""
    global total_tokens_used, total_completion_tokens, response_times, message_count
    
    # Initialize response_tokens to prevent undefined variable errors
    response_tokens = 0
    
    if conversation_history is None:
        conversation_history = []
    
    # Initialize session
    session_data = initialize_session(config, conversation_history)
    
    # Extract session variables
    conversation_history = session_data['conversation_history']
    session_history = session_data['session_history']
    session_start_time = session_data['session_start_time']
    total_tokens_used = session_data['total_tokens_used']
    total_prompt_tokens = session_data['total_prompt_tokens']
    total_completion_tokens = session_data['total_completion_tokens']
    response_times = session_data['response_times']
    message_count = session_data['message_count']
    max_tokens = session_data['max_tokens']
    session_dir = session_data['session_dir']
    last_autosave = session_data['last_autosave']
    autosave_interval = session_data['autosave_interval']
    pricing_info = session_data['pricing_info']
    
    # Create session_stats dictionary for commands that need it
    session_stats = {
        'session_start_time': session_start_time,
        'total_tokens_used': total_tokens_used,
        'total_prompt_tokens': total_prompt_tokens,
        'total_completion_tokens': total_completion_tokens,
        'response_times': response_times,
        'message_count': message_count
    }
    
    # Initialize thinking content tracking
    last_thinking_content = ""
    
    # Get headers for API requests
    headers = get_session_headers(config)

    while True:
        try:
            # Use auto-completion if available, otherwise fallback to regular input
            if HAS_PROMPT_TOOLKIT:
                user_input = get_user_input_with_completion(session_history)
            else:
                user_input = input("User > ")

            # Handle special commands
            # Check if input starts with a command OR contains /upload or /attach
            if user_input.startswith('/') or '/upload' in user_input or '/attach' in user_input:
                # If it contains upload/attach but doesn't start with /, extract the command
                if not user_input.startswith('/') and ('/upload' in user_input or '/attach' in user_input):
                    # Extract the upload/attach command and process it
                    if '/upload' in user_input:
                        # Find the /upload command and everything after it
                        upload_index = user_input.find('/upload')
                        command_part = user_input[upload_index:]
                        user_input = command_part  # Replace user_input with just the command part
                    elif '/attach' in user_input:
                        # Find the /attach command and everything after it
                        attach_index = user_input.find('/attach')
                        command_part = user_input[attach_index:]
                        user_input = command_part  # Replace user_input with just the command part
                
                command = user_input.lower()

                if command == '/exit' or command == '/quit':
                    console.print("[yellow]Exiting chat...[/yellow]")
                    break

                if command == '/help':
                    handle_help_command()
                    continue

                elif command == '/clear':
                    conversation_history = handle_clear_command(conversation_history, config)
                    continue

                elif command == '/new':
                    conversation_history, session_dir = handle_new_command(conversation_history, config, session_dir, session_stats)
                    continue

                elif command == '/save':
                    handle_save_command(user_input, conversation_history, session_dir)
                    continue

                elif command == '/settings':
                    handle_settings_command(config)
                    continue

                elif command == '/tokens':
                    handle_tokens_command(config, session_stats, pricing_info)
                    continue

                elif command == '/speed':
                    handle_speed_command(response_times)
                    continue

                elif command.startswith('/model'):
                    handle_model_command(config)
                    continue

                elif command.startswith('/temperature'):
                    handle_temperature_command(command, config)
                    continue

                elif command.startswith('/system'):
                    handle_system_command(user_input, config, conversation_history)
                    continue

                elif command.startswith('/theme'):
                    handle_theme_command(command, config)
                    continue

                elif command.startswith('/attach') or command.startswith('/upload'):
                    handle_attach_command(user_input, conversation_history)
                    continue

                elif command == '/about':
                    show_about()
                    continue

                elif command == '/update':
                    check_for_updates()
                    continue

                elif command == '/thinking':
                    handle_thinking_command(last_thinking_content)
                    continue

                elif command == '/thinking-mode':
                    handle_thinking_mode_command(config, conversation_history)
                    continue

                elif command in ('/cls', '/clear-screen'):
                    handle_clear_screen_command(config, pricing_info)
                    continue

                else:
                    console.print("[yellow]Unknown command. Type /help for available commands.[/yellow]")
                    continue

            # Check for empty input
            if not user_input.strip():
                console.print("[yellow]Please enter a message or command.[/yellow]")
                continue

            # Count tokens in user input
            input_tokens = count_tokens(user_input)
            total_prompt_tokens += input_tokens

            # Add user message to conversation history
            conversation_history.append({"role": "user", "content": user_input})

            # Get model max tokens
            model_info = get_model_info(config['model'])
            if model_info and 'context_length' in model_info:
                # This is just for display, max_tokens for management is set at the start
                display_max_tokens = model_info['context_length']
            else:
                display_max_tokens = max_tokens

            # Check if we need to trim the conversation history
            conversation_history, trimmed_count = manage_context_window(conversation_history, max_tokens=max_tokens, model_name=config['model'])
            if trimmed_count > 0:
                console.print(f"[yellow]Note: Removed {trimmed_count} earlier messages to stay within the context window.[/yellow]")

            # Clean conversation history for API - remove any messages with invalid fields
            clean_conversation = []
            for msg in conversation_history:
                clean_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                # Handle models that don't support system messages (like Gemma)
                if clean_msg["role"] == "system":
                    # Check if this is a Gemma model that doesn't support system messages
                    if "gemma" in config['model'].lower():
                        # Convert system message to user message with instructions
                        if clean_msg["content"] and clean_msg["content"].strip():
                            clean_msg["role"] = "user"
                            clean_msg["content"] = f"Please follow these instructions: {clean_msg['content']}"
                        else:
                            # Skip empty system messages
                            continue
                    else:
                        # Keep system message for models that support it
                        pass
                
                # Only include valid roles for OpenRouter API
                if clean_msg["role"] in ["system", "user", "assistant"]:
                    clean_conversation.append(clean_msg)

            # Update the API call to use streaming
            data = {
                "model": config['model'],
                "messages": clean_conversation,
                "temperature": config['temperature'],
                "stream": True,
            }

            # Start timing the response
            start_time = time.time()
            timer_display = console.status("[bold cyan]Waiting for response...[/bold cyan]")
            timer_display.start()

            try:
                # Make streaming request
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    stream=True,
                    timeout=60  # Add a timeout
                )

                # Check if the response is successful first
                if response.status_code == 200:
                    # Pass config['thinking_mode'] to stream_response
                    message_content, response_time = stream_response(response, start_time, config['thinking_mode'])

                    # Only add to history if we got actual content
                    if message_content:
                        response_times.append(response_time)

                        # Add assistant response to conversation history
                        conversation_history.append({"role": "assistant", "content": message_content})

                        # Count tokens and update total
                        response_tokens = count_tokens(message_content)
                        total_tokens_used += input_tokens + response_tokens
                        total_completion_tokens += response_tokens
                        
                        # Now process the successful response for display
                        process_api_response(
                            response, config, conversation_history, input_tokens, response_tokens,
                            total_tokens_used, display_max_tokens, message_count, start_time, pricing_info
                        )
                    else:
                        # If we didn't get content but status was 200, something went wrong with streaming
                        console.print("[red]Error: Received empty response from API[/red]")
                        # Remove the user's last message since we didn't get a response
                        if conversation_history and conversation_history[-1]["role"] == "user":
                            conversation_history.pop()
                else:
                    # Handle error response
                    process_api_response(
                        response, config, conversation_history, input_tokens, response_tokens,
                        total_tokens_used, display_max_tokens, message_count, start_time, pricing_info
                    )
            except requests.exceptions.RequestException as e:
                console.print(f"[red]Network error: {str(e)}[/red]")
                # Remove the user's last message since we didn't get a response
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                # Remove the user's last message since we didn't get a response
                if conversation_history and conversation_history[-1]["role"] == "user":
                    conversation_history.pop()
            finally:
                timer_display.stop()

        except KeyboardInterrupt:
            console.print("\n[yellow]Keyboard interrupt detected. Type /exit to quit.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
