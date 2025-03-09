#!/usr/bin/env python
"""
RichCLI main entry point
"""

import os
import sys
from typing import List, Optional

from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .cli.base import BaseUI
from .media.ffmpeg import FFmpegUI
from .media.pdf import PDFToolsUI


class MainUI(BaseUI):
    """Main UI for RichCLI"""

    def __init__(self):
        super().__init__()
        self.tools = {
            "1": ("PDF Tools", PDFToolsUI, "Manipulate PDF files with pdftk and ghostscript"),
            "2": ("FFmpeg UI", FFmpegUI, "Convert media files with FFmpeg"),
            "q": ("Quit", None, "Exit the application"),
        }

    def display_main_menu(self) -> str:
        """Display the main menu and get user selection."""
        self.clear_screen()
        self.display_header("RichCLI", "Terminal User Interface tools for media manipulation")

        table = Table(box=box.SIMPLE)
        table.add_column("Option", style="cyan")
        table.add_column("Tool")
        table.add_column("Description")

        for key, (name, _, description) in self.tools.items():
            table.add_row(key, name, description)

        self.console.print(table)

        choice = Prompt.ask(
            "Select a tool", console=self.console, 
            choices=list(self.tools.keys()),
            default="1"
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
                tool = tool_class()
                
                if hasattr(tool, "main_menu"):
                    tool.main_menu()
                elif hasattr(tool, "run"):
                    tool.run()
                else:
                    self.console.print(f"[red]Error: {name} does not have a run method.[/red]")
                    
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
        arg = sys.argv[1].lower()
        
        # Direct tool launch
        if arg == "pdf":
            PDFToolsUI().main_menu()
            return
        elif arg == "ffmpeg":
            FFmpegUI().run()
            return
        elif arg in ["-h", "--help"]:
            print("RichCLI - Terminal User Interface tools for media manipulation")
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
            print(f"Unknown command: {arg}")
            print("Run 'richcli --help' for usage information")
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