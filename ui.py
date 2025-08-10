import sys
from rich.console import Console
from rich.panel import Panel

# Initialize Rich console
console = Console()

# Check for prompt_toolkit availability
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter, Completion, Completer
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style
    from prompt_toolkit.shortcuts import CompleteStyle
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.filters import Condition
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

class OpenRouterCLICompleter(Completer):
    """Custom completer for OpenRouter CLI commands with descriptions"""
    
    def __init__(self):
        # Define all available commands with their descriptions
        self.commands = {
            'clear': 'Clear the screen and conversation history',
            'chat': 'Manage conversation history. Usage: /chat <list|save|resume> <tag>',
            'compress': 'Compresses the context by replacing it with a summary.',
            'exit': 'Exit the chat',
            'quit': 'Exit the chat', 
            'new': 'Start a new conversation',
            'cls': 'Clear terminal screen',
            'clear-screen': 'Clear terminal screen',
            'save': 'Save conversation to file',
            'settings': 'Adjust model settings',
            'tokens': 'Show token usage statistics',
            'model': 'Change the AI model',
            'temperature': 'Adjust temperature (0.0-2.0)',
            'system': 'View or change system instructions',
            'speed': 'Show response time statistics',
            'theme': 'Change the color theme',
            'about': 'Show information about OpenRouter CLI',
            'update': 'Check for updates',
            'thinking': 'Show last AI thinking process',
            'thinking-mode': 'Toggle thinking mode on/off',
            'attach': 'Share a file with the AI',
            'upload': 'Share a file with the AI',
            'help': 'Show available commands'
        }
        
    def get_completions(self, document, complete_event):
        """Generate completions for the current input"""
        text = document.text_before_cursor
        
        # Only provide completions if text starts with '/'
        if text.startswith('/'):
            # Get the command part without the '/'
            command_part = text[1:].lower()
            
            # Show all matching commands
            for cmd, description in self.commands.items():
                if cmd.lower().startswith(command_part):
                    yield Completion(
                        cmd,
                        start_position=-len(command_part),
                        display_meta=description
                    )

def create_command_completer():
    """Create a command completer for OpenRouter CLI"""
    if not HAS_PROMPT_TOOLKIT:
        return None
    
    return OpenRouterCLICompleter()

def get_user_input_with_completion(history=None):
    """Get user input with command auto-completion and history support"""
    if not HAS_PROMPT_TOOLKIT:
        return input("> ")
    
    try:
        completer = create_command_completer()
        
        # Use provided history or create a new one
        if history is None:
            history = InMemoryHistory()
        
        # Create auto-suggest from history
        auto_suggest = AutoSuggestFromHistory()
        
        # Create key bindings for automatic completion
        bindings = KeyBindings()
        
        @bindings.add('/')
        def _(event):
            """Auto-trigger completion when '/' is typed"""
            event.app.current_buffer.insert_text('/')
            # Force completion menu to show
            event.app.current_buffer.start_completion()
        
        # Add bindings for letters to keep completion active after /
        for char in 'abcdefghijklmnopqrstuvwxyz':
            @bindings.add(char)
            def _(event, char=char):
                """Keep completion active while typing after /"""
                event.app.current_buffer.insert_text(char)
                # Only trigger completion if we're typing after a '/'
                text = event.app.current_buffer.text
                if text.startswith('/') and len(text) > 1:
                    event.app.current_buffer.start_completion()
        
        # Add binding for backspace to retrigger completion
        @bindings.add('backspace')
        def _(event):
            """Handle backspace and retrigger completion if needed"""
            if event.app.current_buffer.text:
                event.app.current_buffer.delete_before_cursor()
                # Retrigger completion if we still have / at the start
                text = event.app.current_buffer.text
                if text.startswith('/'):
                    event.app.current_buffer.start_completion()
        
        # Add binding for Ctrl+Space to manually trigger completion
        @bindings.add('c-space')
        def _(event):
            """Manually trigger completion"""
            event.app.current_buffer.start_completion()
        
        result = prompt(
            "> ",
            completer=completer,
            complete_while_typing=True,
            complete_style="multi-column",
            history=history,
            auto_suggest=auto_suggest,
            enable_history_search=True,
            multiline=False,
            wrap_lines=True,
            key_bindings=bindings
        )
        return result
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception as e:
        # Fallback to regular input if anything goes wrong
        print(f"[Auto-completion error: {e}]")
        return input("> ")

def create_chat_ui():
    """Creates a modern, attractive CLI interface using rich components"""
    # Import here to avoid circular imports
    from app_info import APP_VERSION
    
    console.print(Panel(
        f"[bold blue]Open[/bold blue][bold green]Router[/bold green] [bold cyan]CLI[/bold cyan] [dim]v{APP_VERSION}[/dim]\n\n"
        "Multi-model AI chat • File attachments • Thinking mode • Cost tracking\n\n"
        "Essential Commands:\n"
        "[bold green]/help[/bold green] - Commands list    [bold cyan]/model[/bold cyan] - Switch models    [bold yellow]/theme[/bold yellow] - Appearance\n"
        "[bold magenta]/attach[/bold magenta] - Share files    [bold blue]/thinking[/bold blue] - AI reasoning  [bold red]/clear[/bold red] - New chat\n\n"
        "Ready to start your AI conversation!",
        title="Welcome",
        border_style="green",
        padding=(1, 2)
    ))
