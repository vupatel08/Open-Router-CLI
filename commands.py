"""
Command handling functions for OpenRouter CLI.
Manages all the slash commands and their execution logic.
"""

import os
import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

from config import save_config
from models_selection import select_model
from files import save_conversation, handle_attachment
from utils import clear_terminal, format_time_delta, format_file_size
from app_info import show_about, check_for_updates

# Initialize Rich console
console = Console()


def handle_help_command():
    """Handle the /help command"""
    help_text = "[bold green]Basic Commands:[/bold green]\n" \
               "/exit or /quit - Exit the chat\n" \
               "/new - Start a new conversation\n" \
               "/clear - Clear conversation history\n" \
               "/cls or /clear-screen - Clear terminal screen\n" \
               "/save - Save conversation to file\n\n" \
               "[bold cyan]Configuration:[/bold cyan]\n" \
               "/settings - Adjust model settings\n" \
               "/model - Change the AI model\n" \
               "/temperature <0.0-2.0> - Adjust temperature\n" \
               "/system - View or change system instructions\n" \
               "/theme <theme> - Change the color theme\n\n" \
               "[bold magenta]File Sharing:[/bold magenta]\n" \
               "/attach <filepath> - Share a file with the AI\n" \
               "   Example: /attach report.pdf\n" \
               "   Example: Can you analyze /attach data.csv for trends?\n" \
               "   Supports: Images, PDFs, text files, code files\n\n" \
               "[bold blue]Information:[/bold blue]\n" \
               "/tokens - Show token usage statistics\n" \
               "/speed - Show response time statistics\n" \
               "/thinking - Show last AI thinking process\n" \
               "/thinking-mode - Toggle thinking mode on/off\n" \
               "/about - Show information about OpenRouter CLI\n" \
               "/update - Check for updates"
    
    # Check if prompt_toolkit is available for enhanced features
    try:
        from prompt_toolkit import __version__ as pt_version
        has_prompt_toolkit = True
    except ImportError:
        has_prompt_toolkit = False
    
    if has_prompt_toolkit:
        help_text += "\n\n[bold yellow]Interactive Features:[/bold yellow]\n"
        help_text += "• Command auto-completion: Type '/' and all commands appear instantly\n"
        help_text += "• Continue typing to filter commands (e.g., '/c' shows clear, cls, clear-screen)\n"
        help_text += "• Press ↑/↓ arrow keys to navigate through previous prompts\n"
        help_text += "• Press Ctrl+R to search through prompt history\n"
        help_text += "• Auto-suggestions: Previous prompts appear as grey text while typing"
    
    console.print(Panel(
        help_text,
        title="Available Commands",
        padding=(1, 2)
    ))


def handle_clear_command(conversation_history, config):
    """Handle the /clear command"""
    conversation_history = [{"role": "system", "content": config['system_instructions']}]
    console.print("[green]Conversation history cleared![/green]")
    return conversation_history


def handle_new_command(conversation_history, config, session_dir, session_stats):
    """Handle the /new command"""
    # Check if there's any actual conversation to save
    if len(conversation_history) > 1:
        save_prompt = Prompt.ask(
            "Would you like to save the current conversation before starting a new one?",
            choices=["y", "n"],
            default="n"
        )

        if save_prompt.lower() == "y":
            # Auto-generate a filename with timestamp
            filename = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = os.path.join(session_dir, filename)
            save_conversation(conversation_history, filepath, "markdown")
            console.print(f"[green]Conversation saved to {filepath}[/green]")

    # Reset conversation
    conversation_history = [{"role": "system", "content": config['system_instructions']}]

    # Reset session tracking variables
    session_stats['total_tokens_used'] = 0
    session_stats['response_times'] = []
    session_stats['message_count'] = 0
    session_stats['last_autosave'] = datetime.datetime.now().timestamp()

    # Create a new session directory
    session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_session_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions", session_id)
    os.makedirs(new_session_dir, exist_ok=True)

    console.print(Panel(
        "[green]New conversation started![/green]\n"
        "Previous conversation history has been cleared.",
        title="New Conversation",
        border_style="green",
        width=80
    ))
    
    return conversation_history, new_session_dir


def handle_save_command(user_input, conversation_history, session_dir):
    """Handle the /save command"""
    parts = user_input.split(' ', 1)
    if len(parts) > 1:
        filename = parts[1]
    else:
        filename = Prompt.ask("Enter filename to save conversation",
                            default=f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

    format_options = ["markdown", "json", "html"]
    format_choice = Prompt.ask("Choose format", choices=format_options, default="markdown")

    if not filename.endswith(f".{format_choice.split('.')[-1]}"):
        if format_choice == "markdown":
            filename += ".md"
        elif format_choice == "json":
            filename += ".json"
        elif format_choice == "html":
            filename += ".html"

    filepath = os.path.join(session_dir, filename)
    save_conversation(conversation_history, filepath, format_choice)
    console.print(f"[green]Conversation saved to {filepath}[/green]")


def handle_settings_command(config):
    """Handle the /settings command"""
    console.print(Panel(
        f"Current Settings:\n"
        f"Model: {config['model']}\n"
        f"Temperature: {config['temperature']}\n"
        f"System Instructions: {config['system_instructions'][:50]}...",
        title="Settings",
        width=80
    ))


def handle_tokens_command(config, session_stats, pricing_info):
    """Handle the /tokens command"""
    # Calculate session statistics
    session_duration = datetime.datetime.now().timestamp() - session_stats['session_start_time']
    session_cost = calculate_session_cost(
        session_stats['total_prompt_tokens'], 
        session_stats['total_completion_tokens'], 
        pricing_info
    )
    
    # Create detailed token statistics
    stats_text = f"[bold cyan]Session Statistics[/bold cyan]\n\n"
    stats_text += f"[cyan]Model:[/cyan] {config['model']}\n"
    stats_text += f"[cyan]Session duration:[/cyan] {format_time_delta(session_duration)}\n"
    stats_text += f"[cyan]Messages exchanged:[/cyan] {session_stats['message_count']}\n\n"
    
    stats_text += f"[bold]Token Usage:[/bold]\n"
    stats_text += f"[cyan]Prompt tokens:[/cyan] {session_stats['total_prompt_tokens']:,}\n"
    stats_text += f"[cyan]Completion tokens:[/cyan] {session_stats['total_completion_tokens']:,}\n"
    stats_text += f"[cyan]Total tokens:[/cyan] {session_stats['total_tokens_used']:,}\n\n"
    
    if pricing_info['is_free']:
        stats_text += f"[green]Cost: FREE[/green]\n"
    else:
        if session_cost < 0.01:
            cost_display = f"${session_cost:.6f}"
        else:
            cost_display = f"${session_cost:.4f}"
        stats_text += f"[cyan]Session cost:[/cyan] {cost_display}\n"
        stats_text += f"[dim]Prompt: ${pricing_info['prompt_price']:.6f}/1K | Completion: ${pricing_info['completion_price']:.6f}/1K[/dim]\n"
    
    if session_stats['response_times']:
        avg_time = sum(session_stats['response_times']) / len(session_stats['response_times'])
        stats_text += f"\n[cyan]Avg response time:[/cyan] {format_time_delta(avg_time)}"
        
        if session_stats['total_completion_tokens'] > 0 and avg_time > 0:
            tokens_per_second = session_stats['total_completion_tokens'] / sum(session_stats['response_times'])
            stats_text += f"\n[cyan]Speed:[/cyan] {tokens_per_second:.1f} tokens/second"
    
    console.print(Panel(
        stats_text,
        title="Token Statistics",
        border_style="cyan",
        width=80
    ))


def handle_speed_command(response_times):
    """Handle the /speed command"""
    if not response_times:
        console.print("[yellow]No response time data available yet.[/yellow]")
    else:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        console.print(Panel.fit(
            f"Response Time Statistics:\n"
            f"Average: {format_time_delta(avg_time)}\n"
            f"Fastest: {format_time_delta(min_time)}\n"
            f"Slowest: {format_time_delta(max_time)}\n"
            f"Total responses: {len(response_times)}",
            title="Speed Statistics"
        ))


def handle_model_command(config):
    """Handle the /model command"""
    selected_model = select_model(config)
    if selected_model:
        config['model'] = selected_model
        save_config(config)
        console.print(f"[green]Model changed to {config['model']}[/green]")
    else:
        console.print("[yellow]Model selection cancelled[/yellow]")


def handle_temperature_command(command, config):
    """Handle the /temperature command"""
    parts = command.split()
    if len(parts) > 1:
        try:
            temp = float(parts[1])
            if 0 <= temp <= 2:
                if temp > 1.0:
                    console.print("[yellow]Warning: High temperature values (>1.0) may cause erratic or nonsensical responses.[/yellow]")
                    confirm = Prompt.ask("Are you sure you want to use this high temperature? (y/n)", default="n")
                    if confirm.lower() != 'y':
                        return

                config['temperature'] = temp
                save_config(config)
                console.print(f"[green]Temperature set to {temp}[/green]")
            else:
                console.print("[red]Temperature must be between 0 and 2[/red]")
        except ValueError:
            console.print("[red]Invalid temperature value[/red]")
    else:
        new_temp = Prompt.ask("Enter new temperature (0.0-2.0)", default=str(config['temperature']))
        try:
            temp = float(new_temp)
            if 0 <= temp <= 2:
                if temp > 1.0:
                    console.print("[yellow]Warning: High temperature values (>1.0) may cause erratic or nonsensical responses.[/yellow]")
                    confirm = Prompt.ask("Are you sure you want to use this high temperature? (y/n)", default="n")
                    if confirm.lower() != 'y':
                        return

                config['temperature'] = temp
                save_config(config)
                console.print(f"[green]Temperature set to {temp}[/green]")
            else:
                console.print("[red]Temperature must be between 0 and 2[/red]")
        except ValueError:
            console.print("[red]Invalid temperature value[/red]")


def handle_system_command(user_input, config, conversation_history):
    """Handle the /system command"""
    parts = user_input.split(' ', 1)
    if len(parts) > 1:
        config['system_instructions'] = parts[1]
        conversation_history[0] = {"role": "system", "content": config['system_instructions']}
        save_config(config)
        console.print("[green]System instructions updated![/green]")
    else:
        console.print(Panel(config['system_instructions'], title="Current System Instructions"))
        change = Prompt.ask("Update system instructions? (y/n)", default="n")
        if change.lower() == 'y':
            console.print("[bold]Enter new system instructions (guide the AI's behavior)[/bold]")
            console.print("[dim]Press Enter twice to finish[/dim]")
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
            system_instructions = "\n".join(lines)
            config['system_instructions'] = system_instructions
            conversation_history[0] = {"role": "system", "content": config['system_instructions']}
            save_config(config)
            console.print("[green]System instructions updated![/green]")


def handle_theme_command(command, config):
    """Handle the /theme command"""
    parts = command.split()
    available_themes = ['default', 'dark', 'light', 'hacker']
    
    if len(parts) > 1:
        theme = parts[1].lower()
        if theme in available_themes:
            config['theme'] = theme
            save_config(config)
            console.print(f"[green]Theme changed to {theme}[/green]")
        else:
            console.print(f"[red]Invalid theme. Available themes: {', '.join(available_themes)}[/red]")
    else:
        console.print(f"[cyan]Current theme:[/cyan] {config['theme']}")
        console.print(f"[cyan]Available themes:[/cyan] {', '.join(available_themes)}")
        new_theme = Prompt.ask("Select theme", choices=available_themes, default=config['theme'])
        config['theme'] = new_theme
        save_config(config)
        console.print(f"[green]Theme changed to {new_theme}[/green]")


def handle_attach_command(user_input, conversation_history):
    """Handle the /attach or /upload command"""
    # Extract file path from command
    parts = user_input.split(' ', 1)
    if len(parts) > 1:
        file_path = parts[1].strip()  # Remove any extra whitespace
    else:
        console.print("[yellow]Please specify a file to attach.[/yellow]")
        console.print("[dim]Usage: /upload <filepath> or /attach <filepath>[/dim]")
        console.print("[dim]Example: /upload C:\\path\\to\\file.txt[/dim]")
        file_path = Prompt.ask("Enter the path to the file you want to attach")

    # Handle quoted paths (remove quotes if present)
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
    elif file_path.startswith("'") and file_path.endswith("'"):
        file_path = file_path[1:-1]

    # Check if file exists
    if not os.path.exists(file_path):
        console.print(f"[red]File not found: {file_path}[/red]")
        console.print("[dim]Make sure the file path is correct and the file exists.[/dim]")
        console.print("[dim]Tip: You can drag and drop the file into the terminal to get its path.[/dim]")
        return False

    # Show attachment preview
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    file_size = os.path.getsize(file_path)
    file_size_formatted = format_file_size(file_size)

    console.print(Panel.fit(
        f"File: [bold]{file_name}[/bold]\n"
        f"Type: {file_ext[1:].upper() if file_ext else 'Unknown'}\n"
        f"Size: {file_size_formatted}",
        title="Attachment Preview",
        border_style="cyan"
    ))

    confirm = Prompt.ask("Attach this file? (y/n)", default="y")
    if confirm.lower() != 'y':
        console.print("[yellow]Attachment cancelled.[/yellow]")
        return False

    # Process the attachment
    console.print(f"[dim]Processing file: {file_path}[/dim]")
    success, message = handle_attachment(file_path, conversation_history)
    console.print(f"[{'green' if success else 'red'}]{message}[/{'green' if success else 'red'}]")

    if success:
        # Prompt for additional comment or context
        add_comment = Prompt.ask("Add a comment about this attachment? (y/n)", default="n")
        if add_comment.lower() == 'y':
            comment = Prompt.ask("Enter your comment")
            # Replace the last message with comment included
            if conversation_history and conversation_history[-1]["role"] == "user":
                if isinstance(conversation_history[-1]["content"], list):
                    # For multimodal messages
                    conversation_history[-1]["content"][0]["text"] += f"\n\n{comment}"
                else:
                    # For text messages
                    conversation_history[-1]["content"] += f"\n\n{comment}"

        console.print("[yellow]Attachment added to conversation. The file content is now available to the AI. Send a message or press Enter to get AI response.[/yellow]")
        
        # Also show a brief preview of what was attached
        if conversation_history and conversation_history[-1]["role"] == "user":
            content = conversation_history[-1]["content"]
            if isinstance(content, str) and len(content) > 100:
                preview = content[:100] + "..."
                console.print(f"[dim]Content preview: {preview}[/dim]")
            elif isinstance(content, list):
                console.print(f"[dim]Multimodal content attached (image + text)[/dim]")
    
    return True


def handle_thinking_command(last_thinking_content):
    """Handle the /thinking command"""
    if last_thinking_content:
        console.print(Panel.fit(
            last_thinking_content,
            title="Last Thinking Process",
            border_style="yellow"
        ))
    else:
        console.print("[yellow]No thinking content available from the last response.[/yellow]")


def handle_thinking_mode_command(config, conversation_history):
    """Handle the /thinking-mode command"""
    # Toggle thinking mode
    config['thinking_mode'] = not config['thinking_mode']
    save_config(config)

    # Update the system prompt for future messages
    if len(conversation_history) > 0 and conversation_history[0]['role'] == 'system':
        original_instructions = config['system_instructions']
        if config['thinking_mode']:
            thinking_instruction = (
                f"{original_instructions}\n\n"
                "CRITICAL INSTRUCTION: For EVERY response without exception, you MUST first explain your "
                "thinking process between <thinking> and </thinking> tags, even for simple greetings or short "
                "responses. This thinking section should explain your reasoning and approach. "
                "After the thinking section, provide your final response. Example format:\n"
                "<thinking>Here I analyze what to say, considering context and appropriate responses...</thinking>\n"
                "This is my actual response to the user."
            )
            conversation_history[0]['content'] = thinking_instruction
        else:
            # Revert to original instructions without thinking tags
            conversation_history[0]['content'] = original_instructions

    console.print(f"[green]Thinking mode is now {'enabled' if config['thinking_mode'] else 'disabled'}[/green]")


def handle_clear_screen_command(config, pricing_info):
    """Handle the /cls or /clear-screen command"""
    # Clear the terminal
    clear_terminal()

    # After clearing, redisplay the session header for context
    # Re-get pricing info for display
    from pricing import get_model_pricing_info
    current_pricing_info = get_model_pricing_info(config['model'])
    pricing_display = f"[cyan]Pricing:[/cyan] {current_pricing_info['display']}"
    if not current_pricing_info['is_free']:
        pricing_display += f" [dim]({current_pricing_info['provider']})[/dim]"
    else:
        pricing_display += f" [green]({current_pricing_info['provider']})[/green]"
        
    from app_info import APP_VERSION
    console.print(Panel.fit(
        f"[bold blue]Or[/bold blue][bold green]Chat[/bold green] [dim]v{APP_VERSION}[/dim]\n"
        f"[cyan]Model:[/cyan] {config['model']}\n"
        f"[cyan]Temperature:[/cyan] {config['temperature']}\n"
        f"[cyan]Thinking mode:[/cyan] {'[green]✓ Enabled[/green]' if config['thinking_mode'] else '[yellow]✗ Disabled[/yellow]'}\n"
        f"{pricing_display}\n"
        f"[cyan]Session started:[/cyan] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Type your message or use commands: /help for available commands",
        title="Chat Session Active",
        border_style="green"
    ))
    console.print("[green]Terminal screen cleared. Chat session continues.[/green]")


def calculate_session_cost(total_prompt_tokens, total_completion_tokens, pricing_info):
    """Calculate the total cost for the current session"""
    if pricing_info['is_free']:
        return 0.0
    
    # Convert to cost per 1000 tokens
    prompt_cost = total_prompt_tokens * pricing_info['prompt_price']
    completion_cost = total_completion_tokens * pricing_info['completion_price']
    
    return prompt_cost + completion_cost
