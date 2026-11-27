from argparse import Namespace
from datetime import datetime
from pathlib import Path
import shutil
import subprocess

from zenith.utils import hypr
from zenith.utils.io import fatal, ok, step
from zenith.utils.notify import notify
from zenith.utils.paths import cache_dir, screenshots_dir


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if getattr(self.args, "region", False):
            self.region()
        else:
            self.fullscreen()

    def region(self) -> None:
        if not shutil.which("grim"):
            fatal("grim not found in PATH")
        if not shutil.which("slurp"):
            fatal("slurp not found in PATH")

        # Select region with slurp
        try:
            region = subprocess.check_output(
                ["slurp", "-d", "-b", "#00000088", "-c", "#5895c8ff"],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except subprocess.CalledProcessError:
            return  # User cancelled

        if not region:
            return

        sc_data = subprocess.check_output(["grim", "-g", region, "-"])

        # Copy to clipboard
        if shutil.which("wl-copy"):
            subprocess.run(["wl-copy", "--type", "image/png"], input=sc_data, check=False)

        # Save to cache
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        dest.write_bytes(sc_data)

        # Launch swappy if available
        if shutil.which("swappy"):
            swappy = subprocess.Popen(["swappy", "-f", str(dest)], start_new_session=True)

        action = notify(
            "-i", "camera-photo",
            "--action=open=Open",
            "--action=save=Save to Pictures",
            "Screenshot Taken",
            f"Region copied to clipboard and saved to {dest.name}"
        )

        if action == "save":
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            saved = screenshots_dir / dest.name
            saved.write_bytes(sc_data)
            notify("Screenshot Saved", f"Saved to {saved}")

    def fullscreen(self) -> None:
        if not shutil.which("grim"):
            fatal("grim not found in PATH")

        cmd = ["grim"]
        # Determine focused monitor
        monitors = hypr.monitors()
        focused = next((m for m in monitors if m.get("focused")), None)
        if focused and "name" in focused:
            cmd.extend(["-o", focused["name"]])
        cmd.append("-")

        sc_data = subprocess.check_output(cmd)

        if shutil.which("wl-copy"):
            subprocess.run(["wl-copy", "--type", "image/png"], input=sc_data, check=False)

        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        dest.write_bytes(sc_data)

        action = notify(
            "-i", "camera-photo",
            "--action=open=Open",
            "--action=save=Save to Pictures",
            "Screenshot Taken",
            f"Fullscreen saved to {dest.name} and copied to clipboard"
        )

        if action == "open" and shutil.which("swappy"):
            subprocess.Popen(["swappy", "-f", str(dest)], start_new_session=True)
        elif action == "save":
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            saved = screenshots_dir / dest.name
            saved.write_bytes(sc_data)
            notify("Screenshot Saved", f"Saved to {saved}")
