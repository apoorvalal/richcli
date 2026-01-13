"""
Simple terminal UI for ffmpeg operations using rich.
"""

import os
import subprocess
from typing import Dict, Tuple, Union

from rich import box
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from ..cli.base import BaseUI, NavigationAction


class FFmpegUI(BaseUI):
    """Terminal UI for ffmpeg operations."""

    def __init__(self):
        super().__init__()
        self.command = []
        self.operations = []

        # Common format conversions
        self.formats = {
            "MP4 (H.264)": {"format": "mp4", "vcodec": "libx264", "acodec": "aac"},
            "MP4 (H.265/HEVC)": {"format": "mp4", "vcodec": "libx265", "acodec": "aac"},
            "WebM (VP9)": {
                "format": "webm",
                "vcodec": "libvpx-vp9",
                "acodec": "libopus",
            },
            "GIF": {"format": "gif", "vcodec": "gif", "acodec": "none"},
            "MP3 (audio only)": {
                "format": "mp3",
                "vcodec": "none",
                "acodec": "libmp3lame",
            },
            "WAV (audio only)": {
                "format": "wav",
                "vcodec": "none",
                "acodec": "pcm_s16le",
            },
            "OGG (audio only)": {
                "format": "ogg",
                "vcodec": "none",
                "acodec": "libvorbis",
            },
        }

        # Common resolutions
        self.resolutions = {
            "Original": "",
            "4K (3840x2160)": "3840:2160",
            "1080p (1920x1080)": "1920:1080",
            "720p (1280x720)": "1280:720",
            "480p (854x480)": "854:480",
            "360p (640x360)": "640:360",
        }

    def get_input_file(self) -> str:
        """Prompt user for input file."""
        # List of common media file extensions
        media_extensions = [
            ".mp4", ".avi", ".mov", ".mkv", ".webm", ".gif",
            ".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"
        ]
        
        self.console.print("[bold]Select input media file:[/bold]")
        
        # Use file browser from base class
        self.input_file = self.browse_files(extensions=media_extensions)
        if not self.input_file:
            raise NavigationAction("back")
        return self.input_file

    def get_output_file(self, suggested_output: str) -> str:
        """Prompt user for output file."""
        output_file = Prompt.ask(
            "[bold cyan]Enter output file path[/bold cyan]", default=suggested_output
        )
        self.raise_if_navigation(output_file)
        self.output_file = output_file
        return output_file

    def get_format_conversion(self) -> dict:
        """Select format conversion options."""
        self.clear_screen()
        self.display_header("FFmpeg UI", "Terminal UI for media conversion")

        self.console.print("[bold]Select output format:[/bold]")

        # Display format options
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Format")
        table.add_column("Video Codec")
        table.add_column("Audio Codec")

        for i, (name, details) in enumerate(self.formats.items(), 1):
            vcodec = (
                details["vcodec"] if details["vcodec"] != "none" else "[dim]N/A[/dim]"
            )
            acodec = (
                details["acodec"] if details["acodec"] != "none" else "[dim]N/A[/dim]"
            )
            table.add_row(str(i), name, vcodec, acodec)

        self.console.print(table)

        # Get user selection
        while True:
            try:
                raw_choice = Prompt.ask(
                    "[bold cyan]Enter format number[/bold cyan] (b to go back, q to exit)",
                    default="1",
                )
                action = self.check_navigation(raw_choice)
                if action == "exit":
                    raise NavigationAction("exit")
                if action == "back":
                    raise NavigationAction("back")

                choice = int(raw_choice)

                if 1 <= choice <= len(self.formats):
                    format_name = list(self.formats.keys())[choice - 1]
                    return self.formats[format_name]
                else:
                    self.console.print("[bold red]Invalid choice![/bold red]")
            except NavigationAction:
                raise
            except ValueError:
                self.console.print("[bold red]Please enter a number![/bold red]")

    def get_resolution(self) -> str:
        """Select resolution options."""
        self.clear_screen()
        self.display_header("FFmpeg UI", "Terminal UI for media conversion")

        self.console.print("[bold]Select output resolution:[/bold]")

        # Display resolution options
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Resolution")

        for i, (name, value) in enumerate(self.resolutions.items(), 1):
            table.add_row(str(i), name)

        self.console.print(table)

        # Get user selection
        while True:
            try:
                raw_choice = Prompt.ask(
                    "[bold cyan]Enter resolution number[/bold cyan] (b to go back, q to exit)",
                    default="1",
                )
                action = self.check_navigation(raw_choice)
                if action == "exit":
                    raise NavigationAction("exit")
                if action == "back":
                    raise NavigationAction("back")

                choice = int(raw_choice)

                if 1 <= choice <= len(self.resolutions):
                    resolution_name = list(self.resolutions.keys())[choice - 1]
                    return self.resolutions[resolution_name]
                else:
                    self.console.print("[bold red]Invalid choice![/bold red]")
            except NavigationAction:
                raise
            except ValueError:
                self.console.print("[bold red]Please enter a number![/bold red]")

    def get_trim_options(self) -> Tuple[str, str]:
        """Get trim options from user."""
        self.clear_screen()
        self.display_header("FFmpeg UI", "Terminal UI for media conversion")

        self.console.print("[bold]Trim Video/Audio:[/bold]")
        self.console.print("Leave empty to skip trimming.")
        self.console.print("Format: HH:MM:SS or SS.ms")

        start_time = Prompt.ask(
            "[bold cyan]Enter start time[/bold cyan] (b to go back, q to exit)",
            default="",
        )
        self.raise_if_navigation(start_time)

        end_time = Prompt.ask(
            "[bold cyan]Enter end time[/bold cyan] (or duration, b to go back, q to exit)",
            default="",
        )
        self.raise_if_navigation(end_time)

        return start_time, end_time

    def get_audio_options(self) -> Dict[str, Union[bool, float]]:
        """Get audio processing options."""
        self.clear_screen()
        self.display_header("FFmpeg UI", "Terminal UI for media conversion")

        self.console.print("[bold]Audio Options:[/bold]")

        options = {}

        # Mute audio
        options["mute"] = Confirm.ask(
            "[bold cyan]Mute audio?[/bold cyan]", default=False
        )

        if not options["mute"]:
            # Volume adjustment
            while True:
                volume = Prompt.ask(
                    "[bold cyan]Volume adjustment[/bold cyan] (1.0 = original, 0.5 = half, 2.0 = double, b to go back, q to exit)",
                    default="1.0",
                )
                action = self.check_navigation(volume)
                if action == "exit":
                    raise NavigationAction("exit")
                if action == "back":
                    raise NavigationAction("back")

                try:
                    options["volume"] = float(volume)
                    if options["volume"] >= 0:
                        break
                    else:
                        self.console.print(
                            "[bold red]Please enter a non-negative number![/bold red]"
                        )
                except ValueError:
                    self.console.print(
                        "[bold red]Please enter a valid number![/bold red]"
                    )

        return options

    def build_command(self) -> list:
        """Build the ffmpeg command based on user selections."""
        command = ["ffmpeg", "-i", self.input_file]

        # Add operations arguments
        for operation in self.operations:
            if operation["type"] == "format":
                if operation["vcodec"] != "none":
                    command.extend(["-c:v", operation["vcodec"]])
                if operation["acodec"] != "none":
                    command.extend(["-c:a", operation["acodec"]])

            elif operation["type"] == "resolution":
                if operation["value"]:  # Skip if original resolution
                    command.extend(["-vf", f"scale={operation['value']}"])

            elif operation["type"] == "trim":
                if operation["start"]:
                    command.extend(["-ss", operation["start"]])
                if operation["end"]:
                    if ":" in operation["end"] or "." in operation["end"]:
                        command.extend(["-to", operation["end"]])
                    else:
                        command.extend(["-t", operation["end"]])

            elif operation["type"] == "audio":
                if operation["mute"]:
                    command.extend(["-an"])
                elif operation["volume"] != 1.0:
                    command.extend(["-af", f"volume={operation['volume']:.2f}"])

        # Add output file
        command.append(self.output_file)

        return command

    def preview_command(self) -> bool:
        """Preview the constructed ffmpeg command."""
        self.clear_screen()
        self.display_header("FFmpeg UI", "Terminal UI for media conversion")

        command_str = " ".join(self.command)

        self.console.print("[bold]FFmpeg Command Preview:[/bold]")
        self.console.print(
            Panel(Text(command_str, style="bold green"), box=box.ROUNDED, padding=1)
        )

        self.console.print("\n[bold]Operation summary:[/bold]")
        summary = []

        for op in self.operations:
            if op["type"] == "format":
                summary.append(
                    f"Convert to format with video codec {op['vcodec']} and audio codec {op['acodec']}"
                )
            elif op["type"] == "resolution" and op["value"]:
                summary.append(f"Resize to {op['value'].replace(':', 'x')}")
            elif op["type"] == "trim":
                trim_desc = "Trim: "
                if op["start"]:
                    trim_desc += f"Start at {op['start']}"
                if op["end"]:
                    if op["start"]:
                        trim_desc += ", "
                    if ":" in op["end"] or "." in op["end"]:
                        trim_desc += f"End at {op['end']}"
                    else:
                        trim_desc += f"Duration {op['end']}"
                summary.append(trim_desc)
            elif op["type"] == "audio":
                if op["mute"]:
                    summary.append("Remove audio")
                elif op["volume"] != 1.0:
                    summary.append(f"Adjust volume to {op['volume']:.2f}x")

        for item in summary:
            self.console.print(f"• {item}")

        run = Confirm.ask("\n[bold cyan]Run this command?[/bold cyan]", default=True)

        return run

    def run_command(self) -> None:
        """Execute the ffmpeg command."""
        self.console.print("[bold yellow]Running FFmpeg...[/bold yellow]")

        try:
            # Simple progress display
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            # Print output
            for line in process.stdout:
                if "frame=" in line or "size=" in line or "time=" in line:
                    self.console.print(f"\r[dim]{line.strip()}[/dim]", end="")

            process.wait()

            if process.returncode == 0:
                self.console.print(
                    "\n[bold green]Conversion completed successfully![/bold green]"
                )
                self.command_history.append((" ".join(self.command), "success"))
            else:
                self.console.print("\n[bold red]Conversion failed![/bold red]")
                self.command_history.append((" ".join(self.command), "error"))

        except Exception as e:
            self.console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            self.command_history.append((" ".join(self.command), "error"))

    def run(self) -> None:
        """Main application flow."""
        try:
            self.clear_screen()
            self.display_header("FFmpeg UI", "Terminal UI for media conversion")

            # Check if FFmpeg is installed
            if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
                self.console.print(
                    Panel.fit("[bold red]FFmpeg is not installed![/bold red]", box=box.ROUNDED)
                )
                self.console.print("[yellow]FFmpeg is required for this tool.[/yellow]")
                self.console.print("On Ubuntu/Debian: [green]sudo apt install ffmpeg[/green]")
                self.console.print("On macOS: [green]brew install ffmpeg[/green]")
                self.console.print("On Windows: Download from https://ffmpeg.org/download.html")
                return

            # Get input file
            self.input_file = self.get_input_file()

            # Suggest output file
            basename, ext = os.path.splitext(self.input_file)
            suggested_output = f"{basename}_converted{ext}"
            self.output_file = self.get_output_file(suggested_output)

            # Get format conversion
            format_options = self.get_format_conversion()
            self.operations.append({"type": "format", **format_options})

            # Get resolution if video output
            if format_options["vcodec"] != "none":
                resolution = self.get_resolution()
                self.operations.append({"type": "resolution", "value": resolution})

            # Get trim options
            start_time, end_time = self.get_trim_options()
            if start_time or end_time:
                self.operations.append(
                    {"type": "trim", "start": start_time, "end": end_time}
                )

            # Get audio options if format has audio
            if format_options["acodec"] != "none":
                audio_options = self.get_audio_options()
                self.operations.append({"type": "audio", **audio_options})

            # Build command
            self.command = self.build_command()

            # Preview and confirm
            if self.preview_command():
                self.run_command()
            else:
                self.console.print("[yellow]Command canceled.[/yellow]")
        except NavigationAction as nav:
            if nav.action == "exit":
                self.console.print("[yellow]Exited FFmpeg UI.[/yellow]")
            else:
                self.console.print("[yellow]Returning to main menu.[/yellow]")


def main():
    try:
        ui = FFmpegUI()
        ui.run()
    except KeyboardInterrupt:
        ui.console.print("\nExiting FFmpeg UI. Goodbye!")
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
