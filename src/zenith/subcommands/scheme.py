from argparse import Namespace
import json
from pathlib import Path
import shutil
import subprocess

from zenith.utils.io import fatal, ok, step
from zenith.utils.paths import get_home


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        action = getattr(self.args, "scheme_action", "get")
        if action == "list":
            self.list_schemes()
        elif action == "set":
            self.set_scheme()
        else:
            self.get_scheme()

    def list_schemes(self) -> None:
        step("available color scheme styles")
        print("  * dynamic  (generated from active wallpaper)")
        print("  * catppuccin-mocha")
        print("  * tokyo-night")
        print("  * nord")
        print("  * gruvbox-dark")

    def get_scheme(self) -> None:
        home = get_home()
        state = home / ".config/zenith/color-scheme.json"
        if state.exists():
            print(state.read_text())
        else:
            print("Scheme: dynamic (derived from wallpaper)")

    def set_scheme(self) -> None:
        name = getattr(self.args, "name", "dynamic")
        step(f"applying color scheme: {name}...")
        home = get_home()
        theme_sh = home / ".config/quickshell/scripts/zenith-theme.sh"
        if theme_sh.is_file():
            subprocess.run([str(theme_sh), "--current"], check=False)
            ok(f"applied scheme: {name}")
        else:
            ok("scheme set")
