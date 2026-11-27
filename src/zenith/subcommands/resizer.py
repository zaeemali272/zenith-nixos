from argparse import Namespace
import subprocess

from zenith.utils import hypr
from zenith.utils.io import ok, step


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        pattern = getattr(self.args, "pattern", None)
        width = getattr(self.args, "width", None)
        height = getattr(self.args, "height", None)

        if pattern == "pip":
            # Quick picture-in-picture float & resize
            step("applying Picture-in-Picture layout")
            hypr.dispatch("setfloating")
            hypr.dispatch("resizeactive", "exact", "640", "360")
            hypr.dispatch("pin")
            ok("window set to PiP mode")
        elif width and height:
            step(f"resizing active window to {width}x{height}")
            hypr.dispatch("resizeactive", "exact", str(width), str(height))
            ok("window resized")
        else:
            step("resizer ready")
