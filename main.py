"""
OpenRouter CLI - AI Chat Application
Main entry point for the application.
"""

import sys
from rich.console import Console

from app import initialize_application
from chat import chat_with_model

# Initialize Rich console
console = Console()


def main():
    """Main application entry point"""
    try:
        # Initialize the application
        config, conversation_history = initialize_application()
        
        # Start chat
        chat_with_model(config, conversation_history)
    except Exception as e:
        console.print(f"[red]Critical error during initialization: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting application...")
    except Exception as e:
        console.print(f"[red]Critical error: {str(e)}[/red]")
        sys.exit(1)

