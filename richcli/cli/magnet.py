"""
Magnet feature for dynamically generating UIs for CLI tools based on their help output.
"""

import os
import re
import subprocess
import sys
from typing import Dict, List, Optional

from rich.prompt import Confirm, Prompt
from rich.table import Table

from .base import BaseUI, NavigationAction


class MagnetUI(BaseUI):
    """Dynamically generates a UI for any CLI tool based on its help output."""

    def __init__(self, command_name: str, help_text: str = None):
        super().__init__()
        self.command_name = command_name

        # Get help text if not provided
        if not help_text:
            try:
                result = subprocess.run(
                    [command_name, "-h"], capture_output=True, text=True
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        [command_name, "--help"], capture_output=True, text=True
                    )
                help_text = result.stdout or result.stderr
            except Exception as e:
                self.console.print(
                    f"[red]Error getting help for {command_name}: {str(e)}[/red]"
                )
                help_text = ""

        self.help_text = help_text
        self.options = self._parse_help_text(help_text)
        self.command_args = []

    def _parse_help_text(self, help_text: str) -> List[Dict]:
        """Parse CLI help text to extract options and arguments."""
        options = []
        seen = set()

        def add_option(short_opt: Optional[str], long_opt: Optional[str], arg_name: Optional[str], description: str) -> None:
            """Add an option if it has not already been recorded."""
            key = (short_opt or "", long_opt or "")
            if key in seen:
                return
            seen.add(key)
            options.append(
                {
                    "short": short_opt,
                    "long": long_opt,
                    "arg_name": arg_name,
                    "description": description.strip(),
                    "requires_value": arg_name is not None,
                }
            )

        # Common patterns for option descriptions in help text
        patterns = [
            # -s, --long ARG    Description
            r"^\s*(-\w+),?\s+(--[\w-]+)(?:\s+([A-Z_]+))?\s+(.+)$",
            # --long ARG    Description
            r"^\s*(--[\w-]+)(?:\s+([A-Z_]+))?\s+(.+)$",
            # -s ARG    Description
            r"^\s*(-\w+)(?:\s+([A-Z_]+))?\s+(.+)$",
        ]

        for line in help_text.split("\n"):
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()

                    if len(groups) == 4:  # First pattern with short and long options
                        short_opt, long_opt, arg_name, description = groups
                        add_option(short_opt, long_opt, arg_name, description)
                    elif len(groups) == 3:  # Second pattern with only long option
                        long_opt, arg_name, description = groups
                        add_option(None, long_opt, arg_name, description)
                    break

        if options:
            return options

        # Fallback parsing for usage-style bracketed options (e.g., ssh)
        bracket_tokens = re.findall(r"\[([^\]]+)\]", help_text)
        for token in bracket_tokens:
            token = token.strip()
            if not token or token.lower().startswith("usage"):
                continue

            # Tokens like [-46AaCf] bundle multiple short flags without arguments
            if token.startswith("-") and " " not in token and len(token) > 2:
                packed_flags = token[1:]
                for flag_char in packed_flags:
                    short_opt = f"-{flag_char}"
                    add_option(short_opt, None, None, "Option flag")
                continue

            parts = token.split()
            if not parts:
                continue

            if parts[0].startswith("-"):
                short_opt = parts[0]
                arg_name = parts[1] if len(parts) > 1 else None
                desc = " ".join(parts[1:]) if len(parts) > 1 else "Option flag"
                add_option(short_opt, None, arg_name, desc)

        return options

    def _save_command_template(self):
        """Save the command template as a new UI class."""
        # Create a new Python file for this command
        import os

        module_name = f"{self.command_name.lower().replace('-', '_')}_ui.py"
        output_path = os.path.join(os.getcwd(), module_name)

        with open(output_path, "w") as f:
            f.write(f"""
import os
import subprocess
from typing import Optional

from rich import box
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from richcli.cli.base import BaseUI


class {self.command_name.capitalize()}UI(BaseUI):
    \"\"\"Terminal UI for {self.command_name} operations.\"\"\"

    def __init__(self):
        super().__init__()
        self.command = ["{self.command_name}"]
        self.options = {self.options}

    def run(self) -> None:
        \"\"\"Main application flow.\"\"\"
        self.clear_screen()
        self.display_header("{self.command_name.upper()} UI", "Terminal UI for {self.command_name}")

        # Check if {self.command_name} is installed
        if subprocess.run(["which", "{self.command_name}"], capture_output=True).returncode != 0:
            self.console.print(
                Panel.fit("[bold red]{self.command_name} is not installed![/bold red]", box=box.ROUNDED)
            )
            return

        # Get input files or other required parameters
        # ... implement based on command requirements ...

        # Build command
        self.build_command()

        # Preview and confirm
        if self.preview_command():
            self.run_command()
        else:
            self.console.print("[yellow]Command canceled.[/yellow]")

    def build_command(self) -> list:
        \"\"\"Build the command based on user selections.\"\"\"
        # Implement command building logic
        return self.command

    def preview_command(self) -> bool:
        \"\"\"Preview the constructed command.\"\"\"
        self.clear_screen()
        self.display_header("{self.command_name.upper()} UI", "Terminal UI for {self.command_name}")

        command_str = " ".join(self.command)

        self.console.print("[bold]Command Preview:[/bold]")
        self.console.print(
            Panel(Text(command_str, style="bold green"), box=box.ROUNDED, padding=1)
        )

        run = Confirm.ask("\\n[bold cyan]Run this command?[/bold cyan]", default=True)

        return run

    def run_command(self) -> None:
        \"\"\"Execute the command.\"\"\"
        self.console.print("[bold yellow]Running {self.command_name}...[/bold yellow]")

        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            for line in process.stdout:
                self.console.print(line.strip())

            process.wait()

            if process.returncode == 0:
                self.console.print(
                    "\\n[bold green]Command completed successfully![/bold green]"
                )
                self.command_history.append((" ".join(self.command), "success"))
            else:
                self.console.print("\\n[bold red]Command failed![/bold red]")
                self.command_history.append((" ".join(self.command), "error"))

        except Exception as e:
            self.console.print(f"\\n[bold red]Error:[/bold red] {{str(e)}}")
            self.command_history.append((" ".join(self.command), "error"))


def main():
    \"\"\"Main entry point.\"\"\"
    try:
        ui = {self.command_name.capitalize()}UI()
        ui.run()
    except KeyboardInterrupt:
        print("\\nExiting. Goodbye!")
    except Exception as e:
        print(f"Error: {{str(e)}}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
""")

        self.console.print(
            f"[green]Created template UI for {self.command_name} at {output_path}[/green]"
        )
        return output_path

    def interactive_ui_builder(self) -> None:
        """Interactive builder to construct a UI for this command."""
        self.clear_screen()
        self.display_header(
            f"{self.command_name} UI Builder", "Create a UI for this command"
        )

        # Display parsed options
        self.console.print("[bold]Detected options:[/bold]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option")
        table.add_column("Argument")
        table.add_column("Description")

        for opt in self.options:
            option_text = (
                f"{opt['short']} / {opt['long']}" if opt["short"] else opt["long"]
            )
            arg_text = opt["arg_name"] if opt["arg_name"] else ""
            table.add_row(option_text, arg_text, opt["description"])

        self.console.print(table)

        # Check if stdin is a pipe or terminal
        if not sys.stdin.isatty():
            # If input is piped, default to generating a template
            self.console.print(
                "[yellow]Input is piped, automatically generating template UI[/yellow]"
            )
            self._save_command_template()
            return

        # Generate UI template
        self.console.print("[bold]What would you like to do?[/bold]")
        self.console.print("1. Build and run a command interactively")
        self.console.print("2. Generate a basic UI template for this command")

        choice = Prompt.ask("Choose an option", choices=["1", "2"], default="1")

        if choice == "2":
            self._save_command_template()
        else:
            self._build_interactive_command()

    def _build_interactive_command(self) -> None:
        """Interactively build and execute a command."""

        self.clear_screen()
        self.display_header(
            f"Build {self.command_name} Command", "Interactive command builder"
        )

        command = [self.command_name]

        # Show and optionally change working directory
        current_dir = os.getcwd()
        self.console.print(f"[bold]Current working directory:[/bold] {current_dir}")

        if Confirm.ask("Change working directory?", default=False):
            new_dir = self.browse_files(extensions=None)  # Browse for directories
            if os.path.isdir(new_dir):
                os.chdir(new_dir)
                current_dir = os.getcwd()
                self.console.print(f"[green]Changed to:[/green] {current_dir}")
            else:
                self.console.print(f"[red]Not a directory:[/red] {new_dir}")

        self.console.print("[bold]Build your command step by step:[/bold]")
        self.console.print(
            "[yellow]At each step, choose whether to add a flag, positional argument, or finish[/yellow]"
        )

        while True:
            # Show current command
            self.console.print(f"\n[bold]Current command:[/bold] {' '.join(command)}")

            # Ask what to add next
            self.console.print("\n[bold]What would you like to add next?[/bold]")
            self.console.print("1. Add a flag/option")
            self.console.print("2. Add a positional argument (file, text, etc.)")
            self.console.print("3. Finish building command")
            self.console.print("[dim]Type 'b' to go back or 'q' to exit[/dim]")

            next_step = Prompt.ask(
                "Select", choices=["1", "2", "3", "b", "q"], default="1"
            )

            action = self.check_navigation(next_step)
            if action == "exit":
                return
            if action == "back":
                return

            if next_step == "3":
                break

            elif next_step == "1":
                # Display available options
                table = Table()
                table.add_column("#", style="cyan")
                table.add_column("Option", style="green")
                table.add_column("Description")

                for i, opt in enumerate(self.options, 1):
                    option_text = (
                        f"{opt['short']} / {opt['long']}"
                        if opt["short"]
                        else opt["long"]
                    )
                    table.add_row(str(i), option_text, opt["description"])

                self.console.print(table)

                # Get user choice
                choice = Prompt.ask(
                    "Select option by number (or 'b' to go back, 'q' to exit)",
                    default="1",
                )

                action = self.check_navigation(choice)
                if action == "exit":
                    return
                if action == "back":
                    continue

                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(self.options):
                        opt = self.options[choice_idx]

                        # Add option to command
                        if opt["requires_value"]:
                            value = Prompt.ask(
                                f"Value for {opt['arg_name']} (or 'b' to go back, 'q' to exit)"
                            )
                            action = self.check_navigation(value)
                            if action == "exit":
                                return
                            if action == "back":
                                continue
                            command.append(opt["long"] if opt["long"] else opt["short"])
                            command.append(value)
                        else:
                            command.append(opt["long"] if opt["long"] else opt["short"])
                    else:
                        self.console.print("[red]Invalid option number[/red]")
                except ValueError:
                    self.console.print("[red]Please enter a number[/red]")

            elif next_step == "2":
                # Add a positional argument
                self.console.print("\n[bold]Add positional argument:[/bold]")
                self.console.print(
                    "[yellow]For files, you can type 'browse' to use the file browser.[/yellow]"
                )
                self.console.print("[dim]Type 'b' to go back or 'q' to exit[/dim]")

                argument = Prompt.ask("Argument")

                action = self.check_navigation(argument)
                if action == "exit":
                    return
                if action == "back":
                    continue

                if argument.lower() == "browse":
                    # Use the file browser from BaseUI
                    try:
                        file_path = self.browse_files()
                    except NavigationAction as nav:
                        if nav.action == "exit":
                            return
                        continue
                    if file_path:
                        command.append(file_path)
                        self.console.print(f"[green]Added: {file_path}[/green]")
                else:
                    command.append(argument)
                    self.console.print(f"[green]Added: {argument}[/green]")

        # Execute the command
        self.console.print(f"\n[bold]Final command:[/bold] {' '.join(command)}")

        if Confirm.ask("Run this command?", default=True):
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                )

                for line in process.stdout:
                    self.console.print(line.strip())

                process.wait()

                if process.returncode == 0:
                    self.console.print(
                        "\n[bold green]Command completed successfully![/bold green]"
                    )
                else:
                    self.console.print("\n[bold red]Command failed![/bold red]")

            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {str(e)}")


######################################################################


def run_magnet(command_name, help_text=None):
    """Run the magnet UI for a command."""
    try:
        ui = MagnetUI(command_name, help_text)
        ui.interactive_ui_builder()
    except NavigationAction as nav:
        if nav.action == "exit":
            print("\nExited magnet mode.")
        else:
            print("\nReturning to previous menu.")
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")
    except EOFError:
        # This happens when stdin is piped and we try to read from it again
        print("\nCannot read user input - stdin is being used for help text")
        print("Automatically generating template UI")
        ui._save_command_template()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
