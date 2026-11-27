from argparse import Namespace
import shutil
import subprocess

from zenith.utils.io import fatal


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if not shutil.which("cliphist"):
            fatal("cliphist not found in PATH")
        if not shutil.which("fuzzel"):
            fatal("fuzzel not found in PATH")

        clip = subprocess.check_output(["cliphist", "list"])

        delete_mode = getattr(self.args, "delete", False)
        if delete_mode:
            fuzzel_args = ["--prompt=del > ", "--placeholder=Delete from clipboard"]
        else:
            fuzzel_args = ["--placeholder=Type to search clipboard..."]

        try:
            chosen = subprocess.check_output(
                ["fuzzel", "--dmenu", *fuzzel_args],
                input=clip,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            return  # Cancelled

        if not chosen:
            return

        if delete_mode:
            subprocess.run(["cliphist", "delete"], input=chosen, check=False)
        else:
            decoded = subprocess.check_output(["cliphist", "decode"], input=chosen)
            if shutil.which("wl-copy"):
                subprocess.run(["wl-copy"], input=decoded, check=False)
