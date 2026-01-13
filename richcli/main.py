#!/usr/bin/env python
"""
RichCLI main entry point
"""

import sys

from rich import box
from rich.prompt import Prompt
from rich.table import Table

from .cli.base import BaseUI
from .cli.magnet import run_magnet
from .media.ffmpeg import FFmpegUI
from .media.pdf import PDFToolsUI


class MainUI(BaseUI):
    """Main UI for RichCLI"""

    def __init__(self):
        super().__init__()
        self.tools = {
            "1": (
                "Magnet (Any CLI)",
                "magnet",
                "Parse --help/-h output and build commands interactively",
            ),
            "2": ("FFmpeg UI", FFmpegUI, "Convert media files with FFmpeg"),
            "3": (
                "PDF Tools",
                PDFToolsUI,
                "Manipulate PDF files with pdftk and ghostscript",
            ),
            "q": ("Quit", None, "Exit the application"),
        }

    def display_main_menu(self) -> str:
        """Display the main menu and get user selection."""
        self.clear_screen()
        self.display_header(
            "RichCLI", "Terminal User Interface tools for building CLI calls"
        )

        table = Table(box=box.SIMPLE)
        table.add_column("Option", style="cyan")
        table.add_column("Tool")
        table.add_column("Description")

        for key, (name, _, description) in self.tools.items():
            table.add_row(key, name, description)

        self.console.print(table)

        choice = Prompt.ask(
            "Select a tool",
            console=self.console,
            choices=list(self.tools.keys()),
            default="1",
        )

        return choice

    def run(self) -> None:
        """Run the main UI."""
        while True:
            choice = self.display_main_menu()

            if choice.lower() == "q":
                self.console.print("[bold]Exiting RichCLI. Goodbye![/bold]")
                break

            name, tool_class, _ = self.tools[choice]

            try:
                if tool_class == "magnet":
                    command_name = Prompt.ask(
                        "CLI to wrap",
                        console=self.console,
                        default="",
                        show_default=False,
                    ).strip()

                    action = self.check_navigation(command_name)
                    if action == "exit":
                        break
                    if action == "back":
                        continue

                    if command_name:
                        run_magnet(command_name)
                    else:
                        self.console.print(
                            "[yellow]Please provide a command to wrap.[/yellow]"
                        )
                else:
                    tool = tool_class()

                    if hasattr(tool, "main_menu"):
                        tool.main_menu()
                    elif hasattr(tool, "run"):
                        tool.run()
                    else:
                        self.console.print(
                            f"[red]Error: {name} does not have a run method.[/red]"
                        )

            except KeyboardInterrupt:
                self.console.print(f"\n[yellow]Exiting {name}[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error in {name}: {str(e)}[/red]")
                import traceback

                traceback.print_exc()


def main() -> None:
    """Main entry point for RichCLI."""
    # Handle command line arguments
    if len(sys.argv) > 1:
        raw_arg = sys.argv[1]
        arg = raw_arg.lower()

        # Direct tool launch
        if arg == "pdf":
            PDFToolsUI().main_menu()
            return
        elif arg == "ffmpeg":
            FFmpegUI().run()
            return
        elif arg == "magnet":
            # Check for additional arguments
            if len(sys.argv) > 2:
                command_name = sys.argv[2]

                # Check if we have input from stdin
                help_text = None
                if not sys.stdin.isatty():
                    help_text = sys.stdin.read()
                    # Reset stdin for later input if possible
                    try:
                        # This won't work on all platforms, but it's worth a try
                        sys.stdin = open("/dev/tty")
                    except:
                        # If we can't reopen stdin, we'll handle it in the magnet UI
                        pass

                run_magnet(command_name, help_text)
                return
            else:
                print("Usage: richcli magnet COMMAND_NAME")
                print("       cat COMMAND_HELP | richcli magnet COMMAND_NAME")
                return
        elif arg in ["-h", "--help"]:
            print("RichCLI - Terminal User Interface tools for CLI calls")
            print("\nUsage:")
            print("  richcli           - Launch the main UI")
            print("  richcli pdf       - Launch PDF Tools directly")
            print("  richcli ffmpeg    - Launch FFmpeg UI directly")
            print("  richcli -h/--help - Show this help message")
            print("  richcli -v/--version - Show version information")
            return
        elif arg in ["-v", "--version"]:
            from . import __version__

            print(f"RichCLI version {__version__}")
            return
        else:
            # Fallback: treat any unknown command as a magnet target so users can jump straight in
            help_text = None
            if not sys.stdin.isatty():
                help_text = sys.stdin.read()
                try:
                    sys.stdin = open("/dev/tty")
                except:
                    pass

            run_magnet(raw_arg, help_text)
            return

    # Launch main UI
    try:
        ui = MainUI()
        ui.run()
    except KeyboardInterrupt:
        print("\nExiting RichCLI. Goodbye!")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
