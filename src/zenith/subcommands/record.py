from argparse import Namespace
from datetime import datetime
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

from zenith.utils import hypr
from zenith.utils.io import fatal, ok, step, warn
from zenith.utils.notify import notify
from zenith.utils.paths import recordings_dir, recording_path_file, recording_pid_path


def get_active_recorder() -> str | None:
    for tool in ["gpu-screen-recorder", "wl-screenrec", "wf-recorder"]:
        res = subprocess.run(["pidof", tool], capture_output=True, text=True, check=False)
        if res.returncode == 0:
            return tool
    return None


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        if getattr(self.args, "pause", False):
            self.pause()
            return

        active = get_active_recorder()
        if active:
            self.stop(active)
        else:
            self.start()

    def pause(self) -> None:
        active = get_active_recorder()
        if active == "gpu-screen-recorder":
            subprocess.run(["pkill", "-USR2", "-f", "gpu-screen-recorder"], check=False)
            notify("Screen Recorder", "Toggled pause state")
        else:
            warn("Pause only supported on gpu-screen-recorder")

    def stop(self, tool: str) -> None:
        step(f"stopping {tool} recording...")
        subprocess.run(["pkill", "-SIGINT", "-x", tool], check=False)
        time.sleep(0.5)

        target_file = None
        if recording_path_file.exists():
            try:
                target_file = Path(recording_path_file.read_text().strip())
                recording_path_file.unlink(missing_ok=True)
            except Exception:
                pass
        recording_pid_path.unlink(missing_ok=True)

        if target_file and target_file.exists():
            notify(
                "-i", "screenshooter",
                "--action=watch=Watch",
                "--action=open=Open Folder",
                "Recording Stopped",
                f"Saved to {target_file.name}"
            )
            ok(f"recording saved to {target_file}")
        else:
            notify("Recording Stopped", "Recording saved to Videos/Recordings")
            ok("recording stopped")

    def start(self) -> None:
        recorder_tool = None
        if shutil.which("gpu-screen-recorder"):
            recorder_tool = "gpu-screen-recorder"
        elif shutil.which("wl-screenrec"):
            recorder_tool = "wl-screenrec"
        elif shutil.which("wf-recorder"):
            recorder_tool = "wf-recorder"
        else:
            fatal("No screen recording tool found (install gpu-screen-recorder or wl-screenrec)")

        recordings_dir.mkdir(parents=True, exist_ok=True)
        filename = f"recording_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
        out_path = recordings_dir / filename

        recording_path_file.parent.mkdir(parents=True, exist_ok=True)
        recording_path_file.write_text(str(out_path))

        step(f"starting {recorder_tool}...")
        cmd: list[str] = []

        if recorder_tool == "gpu-screen-recorder":
            cmd = ["gpu-screen-recorder", "-v", "no"]
            if getattr(self.args, "sound", False):
                cmd.extend(["-a", "default_output|default_input"])
            if getattr(self.args, "region", False):
                region = subprocess.check_output(["slurp", "-f", "%wx%h+%x+%y"], text=True).strip()
                cmd.extend(["-w", "region", "-region", region])
            else:
                cmd.extend(["-w", "screen"])
            cmd.extend(["-f", "60", "-o", str(out_path)])

        elif recorder_tool == "wl-screenrec":
            cmd = ["wl-screenrec", "-f", str(out_path)]
            if getattr(self.args, "sound", False):
                cmd.append("--audio")
            if getattr(self.args, "region", False):
                region = subprocess.check_output(["slurp"], text=True).strip()
                cmd.extend(["-g", region])

        else:  # wf-recorder
            cmd = ["wf-recorder", "-f", str(out_path)]
            if getattr(self.args, "sound", False):
                cmd.append("--audio")
            if getattr(self.args, "region", False):
                region = subprocess.check_output(["slurp"], text=True).strip()
                cmd.extend(["-g", region])

        proc = subprocess.Popen(cmd, start_new_session=True)
        recording_pid_path.write_text(str(proc.pid))
        notify("-i", "screenshooter", "Recording Started", f"Recording to {filename}")
        ok(f"recording started (pid {proc.pid})")
