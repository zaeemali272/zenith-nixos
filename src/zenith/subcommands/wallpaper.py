from argparse import Namespace
import os
from pathlib import Path
import random
import shutil
import subprocess

from zenith.utils.io import fatal, ok, step, warn
from zenith.utils.paths import current_wallpaper_file, get_home, wallpapers_dir

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def get_current_wallpaper() -> str | None:
    if current_wallpaper_file.exists():
        try:
            val = current_wallpaper_file.read_text().strip()
            if val and Path(val).exists():
                return val
        except IOError:
            pass
    return None


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if getattr(self.args, "print", False):
            cur = get_current_wallpaper()
            print(cur or "No wallpaper recorded")
        elif getattr(self.args, "file", None):
            self.set_wallpaper(Path(self.args.file))
        elif getattr(self.args, "random", False):
            wp_dir = wallpapers_dir
            if isinstance(self.args.random, str) and Path(self.args.random).is_dir():
                wp_dir = Path(self.args.random)
            self.random_wallpaper(wp_dir)
        else:
            cur = get_current_wallpaper()
            print(cur or "No wallpaper recorded")

    def set_wallpaper(self, wall: Path) -> None:
        if not wall.is_file():
            fatal(f"wallpaper file not found: {wall}")

        wall_resolved = wall.resolve()
        step(f"setting wallpaper: {wall_resolved.name}...")

        # 1. Update awww/swww
        if shutil.which("awww"):
            subprocess.run(
                ["awww", "load", str(wall_resolved)],
                check=False,
                stderr=subprocess.DEVNULL
            )
        elif shutil.which("swww"):
            subprocess.run(
                ["swww", "img", str(wall_resolved), "--transition-type", "grow", "--transition-pos", "center"],
                check=False,
                stderr=subprocess.DEVNULL
            )

        # 2. Record wallpaper
        current_wallpaper_file.write_text(str(wall_resolved))

        # 3. Trigger theme generator if zenith-theme.sh is present
        home = get_home()
        theme_sh = home / ".config/quickshell/scripts/zenith-theme.sh"
        if theme_sh.is_file() and os.access(theme_sh, os.X_OK):
            subprocess.run([str(theme_sh), "--current"], check=False, stderr=subprocess.DEVNULL)

        ok(f"wallpaper updated: {wall_resolved.name}")

    def random_wallpaper(self, directory: Path) -> None:
        if not directory.is_dir():
            fatal(f"directory not found: {directory}")

        candidates = [p for p in directory.rglob("*") if p.suffix.lower() in IMAGE_EXTS]
        if not candidates:
            fatal(f"no images found in {directory}")

        chosen = random.choice(candidates)
        self.set_wallpaper(chosen)
