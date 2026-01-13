"""
PDF Tools - A terminal UI for pdftk and ghostscript operations
"""

import os
import subprocess
import tempfile
from typing import Optional, Tuple

from rich import box
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ..cli.base import BaseUI, NavigationAction


class PDFToolsUI(BaseUI):
    def __init__(self):
        super().__init__()
        self.pdf_files = []
        self.current_pdf = None
        self.scan_for_pdfs()

    def scan_for_pdfs(self) -> None:
        """Scan the current directory for PDF files."""
        self.pdf_files = [f for f in os.listdir(".") if f.lower().endswith(".pdf")]

    def check_tools(self) -> Tuple[bool, bool]:
        """Check if pdftk and ghostscript are installed."""
        pdftk_installed = (
            subprocess.run(["which", "pdftk"], capture_output=True).returncode == 0
        )

        gs_installed = (
            subprocess.run(["which", "gs"], capture_output=True).returncode == 0
        )

        return pdftk_installed, gs_installed

    def select_file(self) -> Optional[str]:
        """Let the user select a PDF file."""
        self.scan_for_pdfs()
        
        # Use file browser from base class
        if self.pdf_files:
            file = self.browse_files(extensions=[".pdf"])
            if not file:
                raise NavigationAction("back")
            self.current_pdf = os.path.basename(file)
            return self.current_pdf

        self.console.print(
            "[yellow]No PDF files found in the current directory.[/yellow]"
        )
        return None

    def main_menu(self) -> None:
        """Display the main menu and handle user selection."""
        choices = {
            "1": ("Select PDF file", self.select_file),
            "2": ("Extract pages", self.extract_pages_menu),
            "3": ("Merge PDFs", self.merge_pdfs_menu),
            "4": ("Compress PDF", self.compress_pdf_menu),
            "5": ("Rotate pages", self.rotate_pages_menu),
            "6": ("Add page numbers", self.add_page_numbers_menu),
            "7": ("Split PDF", self.split_pdf_menu),
            "8": ("View command history", self.view_command_history),
            "9": ("Quit", lambda: None),
        }

        while True:
            try:
                self.clear_screen()
                self.display_header("PDF Tools", "Terminal UI for pdftk and ghostscript")

                if self.current_pdf:
                    self.console.print(
                        f"[bold green]Current PDF:[/bold green] {self.current_pdf}"
                    )

                choice = self.display_menu(choices)

                if choice == "9":
                    break

                description, func = choices[choice]

                # If user selects an operation but hasn't selected a file yet,
                # prompt to select a file first unless the operation is "Merge PDFs"
                if choice not in ["1", "3", "8", "9"] and not self.current_pdf:
                    self.console.print("[yellow]Please select a PDF file first.[/yellow]")
                    self.select_file()
                    if not self.current_pdf:  # If user still hasn't selected a file
                        continue

                result = func()

                if choice == "1" and result:
                    self.console.print(f"[green]Selected:[/green] {result}")

                # Pause to let user read any messages
                if choice != "1":
                    Prompt.ask("\nPress Enter to continue")
            except NavigationAction as nav:
                if nav.action == "exit":
                    self.console.print("[yellow]Exiting PDF Tools.[/yellow]")
                    break
                self.console.print("[yellow]Returning to PDF menu.[/yellow]")

    def extract_pages_menu(self) -> None:
        """Menu for extracting pages from a PDF."""
        self.console.print(
            Panel.fit(f"Extract Pages from {self.current_pdf}", box=box.ROUNDED)
        )

        output_file = Prompt.ask(
            "Output filename", default=f"extract_{self.current_pdf}"
        )
        self.raise_if_navigation(output_file)

        page_range = Prompt.ask(
            "Page range (e.g., 1-5 or 1,3,5 or 1-5,7,9-11)", default="1-end"
        )
        self.raise_if_navigation(page_range)

        # Build the pdftk command
        command = f"pdftk '{self.current_pdf}' cat {page_range} output '{output_file}'"
        
        # Use base class execute_command method
        self.execute_command(
            command, 
            success_message=f"Extracted pages saved to {output_file}"
        )

    def merge_pdfs_menu(self) -> None:
        """Menu for merging multiple PDFs."""
        self.scan_for_pdfs()

        if len(self.pdf_files) < 2:
            self.console.print("[yellow]You need at least 2 PDF files to merge.[/yellow]")
            return

        self.console.print(Panel.fit("Merge PDF Files", box=box.ROUNDED))

        # Display available PDFs with numbers
        table = Table(title="Available PDF Files")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Filename", style="green")

        for idx, filename in enumerate(self.pdf_files, 1):
            table.add_row(str(idx), filename)

        self.console.print(table)

        # Ask user to select files to merge
        selected_indices = Prompt.ask(
            "Select files to merge (numbers separated by commas)",
            default=",".join(str(i) for i in range(1, len(self.pdf_files) + 1)),
        )
        self.raise_if_navigation(selected_indices)

        try:
            indices = [int(idx.strip()) for idx in selected_indices.split(",")]
            selected_files = [
                self.pdf_files[i - 1] for i in indices if 0 < i <= len(self.pdf_files)
            ]
        except (ValueError, IndexError):
            self.console.print("[red]Invalid selection.[/red]")
            return

        if len(selected_files) < 2:
            self.console.print("[yellow]You need to select at least 2 files.[/yellow]")
            return

        output_file = Prompt.ask("Output filename", default="merged.pdf")
        self.raise_if_navigation(output_file)

        # Build the pdftk command
        file_args = " ".join([f"'{f}'" for f in selected_files])
        command = f"pdftk {file_args} cat output '{output_file}'"

        # Use base class execute_command method
        self.execute_command(
            command, 
            success_message=f"Merged PDF saved to {output_file}"
        )

    def compress_pdf_menu(self) -> None:
        """Menu for compressing a PDF."""
        self.console.print(Panel.fit(f"Compress {self.current_pdf}", box=box.ROUNDED))

        output_file = Prompt.ask(
            "Output filename", default=f"compressed_{self.current_pdf}"
        )
        self.raise_if_navigation(output_file)

        # Ask for quality level
        quality_options = {
            "1": ("Screen", "/screen"),
            "2": ("Ebook", "/ebook"),
            "3": ("Printer", "/printer"),
            "4": ("Prepress", "/prepress"),
            "5": ("Default", "/default"),
        }

        table = Table()
        table.add_column("Option", style="cyan")
        table.add_column("Quality Level")
        table.add_column("Description")

        table.add_row("1", "Screen [lowest]", "Low quality, smaller size (72 dpi)")
        table.add_row("2", "Ebook", "Medium quality, medium size (150 dpi)")
        table.add_row("3", "Printer", "Higher quality, larger size (300 dpi)")
        table.add_row("4", "Prepress", "High quality, larger size (300+ dpi)")
        table.add_row("5", "Default", "Ghostscript default settings")

        self.console.print(table)

        quality = Prompt.ask(
            "Select quality level (b to go back, q to exit)",
            choices=list(quality_options.keys()) + ["b", "q"],
            default="2",
        )
        action = self.check_navigation(quality)
        if action:
            raise NavigationAction(action)

        # Build the Ghostscript command
        quality_name, quality_setting = quality_options[quality]
        gs_command = (
            f"gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={quality_setting} "
            f"-dNOPAUSE -dQUIET -dBATCH -sOutputFile='{output_file}' '{self.current_pdf}'"
        )

        # Show the quality info
        self.console.print(f"[italic]Quality level:[/italic] {quality_name}")

        # Use base class execute_command method
        if self.execute_command(
            gs_command, 
            success_message=f"Compressed PDF saved to {output_file}"
        ):
            # Get original and new file sizes
            orig_size = os.path.getsize(self.current_pdf)
            new_size = os.path.getsize(output_file)
            reduction = (1 - (new_size / orig_size)) * 100

            self.console.print(f"Original size: {orig_size / 1024:.1f} KB")
            self.console.print(f"New size: {new_size / 1024:.1f} KB")
            self.console.print(f"Reduction: {reduction:.1f}%")

    def rotate_pages_menu(self) -> None:
        """Menu for rotating pages in a PDF."""
        self.console.print(Panel.fit(f"Rotate Pages in {self.current_pdf}", box=box.ROUNDED))

        output_file = Prompt.ask(
            "Output filename", default=f"rotated_{self.current_pdf}"
        )
        self.raise_if_navigation(output_file)

        page_range = Prompt.ask(
            "Page range (e.g., 1-5 or 1,3,5 or 1-5,7,9-11)", default="1-end"
        )
        self.raise_if_navigation(page_range)

        rotation_options = {
            "1": "north",  # No rotation
            "2": "east",  # 90 degrees clockwise
            "3": "south",  # 180 degrees
            "4": "west",  # 90 degrees counterclockwise
        }

        table = Table()
        table.add_column("Option", style="cyan")
        table.add_column("Direction")
        table.add_column("Degrees")

        table.add_row("1", "North", "0° (no rotation)")
        table.add_row("2", "East", "90° clockwise")
        table.add_row("3", "South", "180°")
        table.add_row("4", "West", "90° counterclockwise")

        self.console.print(table)

        rotation = Prompt.ask(
            "Select rotation (b to go back, q to exit)",
            choices=list(rotation_options.keys()) + ["b", "q"],
            default="2",
        )
        action = self.check_navigation(rotation)
        if action:
            raise NavigationAction(action)

        rotation_value = rotation_options[rotation]

        # Build the pdftk command
        command = f"pdftk '{self.current_pdf}' cat {page_range}{rotation_value} output '{output_file}'"

        # Use base class execute_command method
        self.execute_command(
            command, 
            success_message=f"Rotated PDF saved to {output_file}"
        )

    def add_page_numbers_menu(self) -> None:
        """Menu for adding page numbers to a PDF."""
        self.console.print(
            Panel.fit(f"Add Page Numbers to {self.current_pdf}", box=box.ROUNDED)
        )

        output_file = Prompt.ask(
            "Output filename", default=f"numbered_{self.current_pdf}"
        )
        self.raise_if_navigation(output_file)

        # This is more complex and requires multiple steps:
        # 1. Create a temporary PostScript file with page numbers
        # 2. Overlay it on the original PDF

        position_options = {
            "1": ("Bottom Center", "center", "10"),
            "2": ("Bottom Right", "right", "10"),
            "3": ("Bottom Left", "left", "10"),
            "4": ("Top Center", "center", "790"),
            "5": ("Top Right", "right", "790"),
            "6": ("Top Left", "left", "790"),
        }

        table = Table()
        table.add_column("Option", style="cyan")
        table.add_column("Position")

        for key, (pos_name, _, _) in position_options.items():
            table.add_row(key, pos_name)

        self.console.print(table)

        position = Prompt.ask(
            "Select page number position (b to go back, q to exit)",
            choices=list(position_options.keys()) + ["b", "q"],
            default="1",
        )
        action = self.check_navigation(position)
        if action:
            raise NavigationAction(action)

        pos_name, halign, vpos = position_options[position]

        start_value = Prompt.ask(
            "Starting page number (b to go back, q to exit)", default="1"
        )
        action = self.check_navigation(start_value)
        if action:
            raise NavigationAction(action)
        try:
            start_num = int(start_value)
        except ValueError:
            self.console.print("[red]Please enter a valid starting number.[/red]")
            return

        # Create a temporary directory for the intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create a text file with PostScript commands to add page numbers
            ps_file = os.path.join(temp_dir, "pagenumbers.ps")

            with open(ps_file, "w") as f:
                f.write(f"""%!PS
/Helvetica findfont 12 scalefont setfont
/pagecount {{
  /pagenum exch def
  {halign}show
}} def
/center {{
  dup stringwidth pop 2 div
  306 exch sub {vpos} moveto
}} def
/right {{
  dup stringwidth pop
  592 exch sub {vpos} moveto
}} def
/left {{
  20 {vpos} moveto
}} def
<<
  /EndPage {{
    exch pop 0 eq
    {{ false }}
    {{
      dup {start_num} add
      10 string cvs pagecount
      true
    }} ifelse
  }} bind
>> setpagedevice
""")

            # Step 2: Use Ghostscript to overlay the page numbers
            gs_command = (
                f"gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile='{output_file}' "
                f"-dAutoRotatePages=/None -dAutoFilterColorImages=false "
                f"-dColorImageFilter=/FlateEncode -f '{ps_file}' '{self.current_pdf}'"
            )

            # Show position info
            self.console.print(f"[italic]Position:[/italic] {pos_name}")
            
            # Use base class execute_command method
            self.execute_command(
                gs_command, 
                success_message=f"PDF with page numbers saved to {output_file}"
            )

    def split_pdf_menu(self) -> None:
        """Menu for splitting a PDF into individual pages or chunks."""
        self.console.print(Panel.fit(f"Split {self.current_pdf}", box=box.ROUNDED))

        split_options = {"1": "Individual pages", "2": "Page ranges"}

        for key, desc in split_options.items():
            self.console.print(f"[cyan]{key}[/cyan]: {desc}")

        choice = Prompt.ask(
            "Select split method (b to go back, q to exit)",
            choices=list(split_options.keys()) + ["b", "q"],
            default="1",
        )
        action = self.check_navigation(choice)
        if action:
            raise NavigationAction(action)

        if choice == "1":
            # Split into individual pages
            output_pattern = Prompt.ask(
                "Output filename pattern (use %d for page number)",
                default="page_%04d.pdf",
            )
            self.raise_if_navigation(output_pattern)

            command = f"pdftk '{self.current_pdf}' burst output '{output_pattern}'"

            # Use base class execute_command method
            success = self.execute_command(
                command, 
                success_message="PDF split into individual pages"
            )
            
            # Remove the doc_data.txt file if command was successful
            if success and os.path.exists("doc_data.txt"):
                os.remove("doc_data.txt")
        else:
            # Split by page ranges
            self.console.print(
                "Enter page ranges (one per line, format: 'output_name.pdf 1-5,8,11-13')"
            )
            self.console.print("Enter an empty line when done.")

            ranges = []
            while True:
                range_input = Prompt.ask("Page range (or 'b' to go back, 'q' to exit)", default="")
                action = self.check_navigation(range_input)
                if action == "exit":
                    raise NavigationAction("exit")
                if action == "back":
                    break
                if not range_input:
                    break
                ranges.append(range_input)

            if not ranges:
                self.console.print("[yellow]No page ranges specified.[/yellow]")
                return

            for page_range in ranges:
                try:
                    output_file, pages = page_range.split(" ", 1)

                    command = (
                        f"pdftk '{self.current_pdf}' cat {pages} output '{output_file}'"
                    )

                    self.execute_command(
                        command, 
                        success_message=f"Created {output_file}"
                    )
                except ValueError:
                    self.console.print(f"[red]Invalid format: {page_range}[/red]")


def main():
    # Check if required tools are installed
    pdf_ui = PDFToolsUI()
    pdftk_installed, gs_installed = pdf_ui.check_tools()

    if not pdftk_installed or not gs_installed:
        pdf_ui.console.print(
            Panel.fit("[bold red]Missing required tools![/bold red]", box=box.ROUNDED)
        )

        if not pdftk_installed:
            pdf_ui.console.print("[yellow]pdftk is not installed.[/yellow]")
            pdf_ui.console.print("On Ubuntu/Debian: [green]sudo apt install pdftk[/green]")
            pdf_ui.console.print("On macOS: [green]brew install pdftk-java[/green]")
            pdf_ui.console.print(
                "On Windows: Download from https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/\n"
            )

        if not gs_installed:
            pdf_ui.console.print("[yellow]ghostscript is not installed.[/yellow]")
            pdf_ui.console.print(
                "On Ubuntu/Debian: [green]sudo apt install ghostscript[/green]"
            )
            pdf_ui.console.print("On macOS: [green]brew install ghostscript[/green]")
            pdf_ui.console.print(
                "On Windows: Download from https://www.ghostscript.com/download/gsdnld.html\n"
            )

        pdf_ui.console.print("Please install the required tools and try again.")
        return

    try:
        pdf_ui.main_menu()
    except KeyboardInterrupt:
        pdf_ui.console.print("\nExiting PDF Tools. Goodbye!")
    except Exception as e:
        pdf_ui.console.print(f"[bold red]An error occurred:[/bold red] {str(e)}")


if __name__ == "__main__":
    main()
