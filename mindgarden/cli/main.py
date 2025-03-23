"""
Main CLI interface for MindGarden.
"""

import typer
from rich.console import Console
from rich.prompt import Prompt

from mindgarden.agent.agent import Agent
from mindgarden.config.settings import get_config

app = typer.Typer(help="MindGarden CLI")
console = Console()


def check_api_key() -> bool:
    """Check if OpenAI API key is configured."""
    config = get_config()
    if not config.openai_api_key:
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY is not set in the environment.")
        console.print("Please set it using: export OPENAI_API_KEY=your_key_here")
        return False
    return True


@app.command()
def chat(debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode")):
    """Start a chat session with Quinn."""
    if not check_api_key():
        return
    
    config = get_config()
    agent = Agent()
    
    console.print(f"[bold green]{config.agent_name}[/bold green]: Hello! I'm {config.agent_name}, your personal assistant. How can I help you today?")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print(f"[bold green]{config.agent_name}[/bold green]: Goodbye! Have a great day!")
                break
            
            response = agent.process_message(user_input)
            console.print(f"\n[bold green]{config.agent_name}[/bold green]: {response}")
        
        except KeyboardInterrupt:
            console.print("\n[bold green]{config.agent_name}[/bold green]: Goodbye! Have a great day!")
            break
        except Exception as e:
            if debug:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
            else:
                console.print("[bold red]Error:[/bold red] Something went wrong. Please try again.")


@app.command()
def version():
    """Show the MindGarden version."""
    from mindgarden import __version__
    console.print(f"MindGarden version: [bold]{__version__}[/bold]")


def main():
    """Run the MindGarden CLI."""
    app() 