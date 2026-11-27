from argparse import Namespace
import shutil
import subprocess

from zenith.utils.io import fatal, ok

SYMBOLS = [
    ("🚀", "rocket"),
    ("✨", "sparkles"),
    ("🔥", "fire"),
    ("🎉", "party"),
    ("❤️", "heart"),
    ("👍", "thumbs up"),
    ("💡", "light bulb"),
    ("⚡", "lightning"),
    ("⭐", "star"),
    ("📦", "package"),
    ("🛠️", "tools"),
    ("🔍", "search"),
]


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if not shutil.which("fuzzel"):
            fatal("fuzzel not found in PATH")

        items = "\n".join(f"{glyph} {name}" for glyph, name in SYMBOLS)

        try:
            chosen = subprocess.check_output(
                ["fuzzel", "--dmenu", "--placeholder=Select symbol..."],
                input=items.encode(),
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except subprocess.CalledProcessError:
            return

        if not chosen:
            return

        glyph = chosen.split()[0]
        if shutil.which("wl-copy"):
            subprocess.run(["wl-copy"], input=glyph.encode(), check=False)
            ok(f"copied {glyph} to clipboard")
