"""
Application information and constants for OpenRouter CLI.
Contains version info, URLs, and display functions.
"""

import json
import webbrowser
import urllib.request
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from packaging import version

# Initialize Rich console
console = Console()

# Constants for the application
APP_NAME = "OpenRouter CLI"
APP_VERSION = "1.2.9"
REPO_URL = "https://github.com/oop7/OrChat"
API_URL = "https://api.github.com/repos/oop7/OrChat/releases/latest"


def show_about():
    """Display information about OpenRouter CLI"""
    console.print(Panel.fit(
        f"[bold blue]Open[/bold blue][bold green]Router[/bold green] [bold cyan]CLI[/bold cyan] [dim]v{APP_VERSION}[/dim]\n\n"
        "A powerful CLI for chatting with AI models through OpenRouter.\n\n"
        f"[link={REPO_URL}]{REPO_URL}[/link]\n\n"
        "Created by OOP7\n"
        "Licensed under MIT License",
        title="About OpenRouter CLI",
        border_style="blue"
    ))


def check_for_updates():
    """Check GitHub for newer versions of OpenRouter CLI"""
    console.print("[bold cyan]Checking for updates...[/bold cyan]")
    try:
        with urllib.request.urlopen(API_URL) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get('tag_name', 'v0.0.0').lstrip('v')

                if version.parse(latest_version) > version.parse(APP_VERSION):
                    console.print(Panel.fit(
                        f"[yellow]A new version of OpenRouter CLI is available![/yellow]\n"
                        f"Current version: [cyan]{APP_VERSION}[/cyan]\n"
                        f"Latest version: [green]{latest_version}[/green]\n\n"
                        f"Update at: {REPO_URL}/releases",
                        title="Update Available",
                        border_style="yellow"
                    ))

                    open_browser = Prompt.ask("Open release page in browser?", choices=["y", "n"], default="n")
                    if open_browser.lower() == "y":
                        webbrowser.open(f"{REPO_URL}/releases")
                else:
                    console.print("[green]You are using the latest version of OpenRouter CLI![/green]")
            else:
                console.print("[yellow]Could not check for updates. Server returned status "
                            f"code {response.getcode()}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Could not check for updates: {str(e)}[/yellow]")
