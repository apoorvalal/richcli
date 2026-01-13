"""
Base class for RichCLI applications
"""

import os
from typing import Callable, Dict, List, Optional, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text


class NavigationAction(Exception):
    """Signal user navigation (back or exit) during interactive prompts."""

    def __init__(self, action: str):
        super().__init__(action)
        self.action = action


class BaseUI:
    """Base UI class for RichCLI applications."""

    def __init__(self):
        self.console = Console()
        self.command_history = []
        self.input_file = None
        self.output_file = None

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def check_navigation(self, value: str) -> Optional[str]:
        """Return navigation action if user typed back/exit."""
        if not isinstance(value, str):
            return None
        normalized = value.strip().lower()
        if normalized in {"b", "back"}:
            return "back"
        if normalized in {"q", "quit", "exit"}:
            return "exit"
        return None

    def raise_if_navigation(self, value: str) -> None:
        """Raise NavigationAction if value requests back/exit."""
        action = self.check_navigation(value)
        if action:
            raise NavigationAction(action)

    def display_header(self, title: str, subtitle: str = "") -> None:
        """Display the application header.
        
        Args:
            title: Main title for the header
            subtitle: Optional subtitle
        """
        content = Text(title, style="bold white on blue", justify="center")
        if subtitle:
            content.append("\n" + subtitle)
            
        self.console.print(
            Panel.fit(
                content,
                box=box.ROUNDED,
                padding=(1, 4),
                title=f"Terminal UI for {title}",
            )
        )
    
    def display_menu(self, choices: Dict[str, Tuple[str, Callable]]) -> str:
        """Display menu options and get user choice.
        
        Args:
            choices: Dictionary mapping keys to (description, function) tuples
            
        Returns:
            User's menu selection
        """
        table = Table(box=box.SIMPLE)
        table.add_column("Option", style="cyan")
        table.add_column("Description")

        for key, (description, _) in choices.items():
            table.add_row(key, description)

        self.console.print(table)

        choice = Prompt.ask(
            "Select an option", console=self.console, choices=list(choices.keys())
        )
        
        return choice
    
    def browse_files(self, extensions: List[str] = None) -> str:
        """Browse files in a directory and select one.
        
        Args:
            extensions: List of file extensions to show (e.g. ['.pdf', '.mp4'])
            
        Returns:
            Path to selected file
        """
        current_dir = os.getcwd()
        while True:
            self.clear_screen()
            
            # Display current directory
            self.console.print(f"[bold]Current directory:[/bold] {current_dir}")

            # List files and directories
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Type", style="dim", width=4)
            table.add_column("Name")

            # Add parent directory
            table.add_row("[D]", "[yellow]..[/yellow]")

            # List contents
            try:
                for item in sorted(os.listdir(current_dir)):
                    path = os.path.join(current_dir, item)
                    if os.path.isdir(path):
                        table.add_row("[D]", f"[yellow]{item}/[/yellow]")
                    else:
                        # Filter by extensions if provided
                        if extensions:
                            ext = os.path.splitext(item)[1].lower()
                            if ext in extensions:
                                table.add_row("[F]", item)
                        else:
                            table.add_row("[F]", item)
            except PermissionError:
                self.console.print("[bold red]Permission denied[/bold red]")
                current_dir = os.path.dirname(current_dir)
                continue

            self.console.print(table)

            choice = Prompt.ask(
                "[bold cyan]Enter file/directory name, '..' for parent, 'b' to go back, or full path[/bold cyan]",
                default="..",
            )

            action = self.check_navigation(choice)
            if action == "exit":
                raise NavigationAction("exit")
            if action == "back":
                return None

            if choice == "..":
                current_dir = os.path.dirname(current_dir)
            elif os.path.isabs(choice) and os.path.exists(choice):
                if os.path.isdir(choice):
                    current_dir = choice
                else:
                    return choice
            else:
                # Check if it's a directory
                dir_path = os.path.join(current_dir, choice)
                if os.path.isdir(dir_path):
                    current_dir = dir_path
                elif os.path.isfile(dir_path):
                    return dir_path
                else:
                    self.console.print("[bold red]Invalid selection[/bold red]")
    
    def execute_command(self, command: str, success_message: str = "Command executed successfully") -> bool:
        """Execute a command and track its history.
        
        Args:
            command: Command to execute
            success_message: Message to show on success
            
        Returns:
            True if command succeeded, False otherwise
        """
        # Show the command and ask for confirmation
        self.console.print(f"[bold]Command:[/bold] {command}")

        if Confirm.ask("Run this command?"):
            self.console.print("[bold]Running command...[/bold]")
            
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                self.console.print(f"[green]Success![/green] {success_message}")
                self.command_history.append((command, "success"))
                return True
            else:
                self.console.print(f"[red]Error:[/red] {result.stderr}")
                self.command_history.append((command, "error"))
                return False
        return False

    def view_command_history(self) -> None:
        """Display the command history."""
        if not self.command_history:
            self.console.print("[yellow]No commands have been executed yet.[/yellow]")
            return

        self.console.print(Panel.fit("Command History", box=box.ROUNDED))

        table = Table()
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Command", style="green")
        table.add_column("Status", justify="center")

        for idx, (command, status) in enumerate(self.command_history, 1):
            status_style = "green" if status == "success" else "red"
            table.add_row(
                str(idx), command, f"[{status_style}]{status}[/{status_style}]"
            )

        self.console.print(table)
