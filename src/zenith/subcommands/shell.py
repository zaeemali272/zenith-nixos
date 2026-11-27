from argparse import Namespace
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from zenith.utils import hypr
from zenith.utils.io import fatal, ok, step, warn
from zenith.utils.paths import active_shell_path, get_home, zenith_config_dir


def reset_shell_themes() -> None:
    home = get_home()
    # 1. Clean up stray GTK Thunar styles
    for p in [home / ".config/gtk-3.0/thunar.css", home / ".config/gtk-4.0/thunar.css"]:
        try:
            if p.exists():
                p.unlink()
        except OSError:
            pass

    # 2. Reset duplicate fuzzel color blocks if any
    fuzzel_ini = home / ".config/fuzzel/fuzzel.ini"
    if fuzzel_ini.exists():
        try:
            subprocess.run(
                ["sed", "-i", "/^\\[colors\\]/{n;:a;/^\\[/!{d;n;ba;}}", str(fuzzel_ini)],
                check=False,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    # 3. Reload Thunar daemon cleanly
    if shutil.which("thunar"):
        subprocess.run(["thunar", "-q"], check=False, stderr=subprocess.DEVNULL)


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        action = getattr(self.args, "action", None)
        if not action:
            if getattr(self.args, "restart", False):
                action = "restart"
            elif getattr(self.args, "kill", False):
                action = "kill"
            elif getattr(self.args, "show", False):
                action = "show"
            elif getattr(self.args, "log", False):
                action = "log"
            elif getattr(self.args, "message", None):
                action = "call"
            else:
                action = "start"

        if action in ["list", "ls"]:
            self.list_shells()
        elif action in ["switch", "use"]:
            self.switch_shell(getattr(self.args, "target", None) or (self.args.message[0] if self.args.message else None))
        elif action == "restart":
            self.restart_shell()
        elif action == "kill":
            self.stop_instances()
        elif action == "show":
            self.print_ipc()
        elif action == "log":
            self.print_log()
        elif action == "call":
            self.call_ipc()
        else:
            self.start_shell()

    def get_active_shell(self) -> str:
        if active_shell_path.exists():
            try:
                name = active_shell_path.read_text().strip()
                if name:
                    return name
            except IOError:
                pass
        return "zenith"

    def list_shells(self) -> None:
        step("available desktop shells")
        active = self.get_active_shell()
        for s in ["zenith", "caelestia", "end-4"]:
            if s == active:
                print(f"  * \033[1;32m{s}\033[0m (active)")
            else:
                print(f"    {s}")

    def stop_instances(self) -> None:
        step("stopping shell instances")
        # Quickshell
        if shutil.which("qs"):
            subprocess.run(["qs", "kill"], check=False, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        # launch.sh stop
        launch_sh = get_home() / ".config/quickshell/launch.sh"
        if launch_sh.is_file() and os.access(launch_sh, os.X_OK):
            subprocess.run([str(launch_sh), "stop"], check=False, stderr=subprocess.DEVNULL)

        subprocess.run(["pkill", "-f", "^quickshell( |$)"], check=False, stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "caelestia-shell"], check=False, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        ok("stopped running shells")

    def start_shell(self) -> None:
        active = self.get_active_shell()
        step(f"starting {active} shell")
        daemon = getattr(self.args, "daemon", False) or True

        if active == "caelestia" and shutil.which("caelestia-shell"):
            cmd = ["caelestia-shell", "-d"] if daemon else ["caelestia-shell"]
            subprocess.Popen(cmd, start_new_session=True)
            ok("caelestia shell started")
            return

        if active == "end-4":
            if shutil.which("end4-shell"):
                cmd = ["end4-shell", "-d"] if daemon else ["end4-shell"]
                subprocess.Popen(cmd, start_new_session=True)
                ok("end-4 shell started")
                return

        # Default: zenith
        launch_sh = get_home() / ".config/quickshell/launch.sh"
        if launch_sh.is_file() and os.access(launch_sh, os.X_OK):
            subprocess.run([str(launch_sh), "start"], check=False)
        else:
            subprocess.Popen(["quickshell", "-d"], start_new_session=True)
        ok("zenith shell started")

    def restart_shell(self) -> None:
        step("restarting the active desktop shell")
        active = self.get_active_shell()
        self.stop_instances()
        time.sleep(0.5)

        if active == "caelestia" and shutil.which("caelestia-shell"):
            subprocess.Popen(["caelestia-shell", "-d"], start_new_session=True)
            ok("caelestia shell restarted")
        elif active == "end-4":
            if shutil.which("end4-shell"):
                subprocess.Popen(["end4-shell", "-d"], start_new_session=True)
            else:
                subprocess.Popen(["quickshell", "-d"], start_new_session=True)
            ok("end-4 shell restarted")
        else:
            launch_sh = get_home() / ".config/quickshell/launch.sh"
            if launch_sh.is_file() and os.access(launch_sh, os.X_OK):
                subprocess.run([str(launch_sh), "restart"], check=False)
            else:
                subprocess.Popen(["quickshell", "-d"], start_new_session=True)
            ok("zenith shell restarted")

    def switch_shell(self, target: str | None) -> None:
        if not target or target not in ["zenith", "caelestia", "end-4"]:
            fatal(f"unknown shell: {target} (available: zenith, caelestia, end-4)")

        step(f"switching desktop shell to {target}...")
        zenith_config_dir.mkdir(parents=True, exist_ok=True)
        active_shell_path.write_text(target)

        self.stop_instances()
        reset_shell_themes()

        home = get_home()
        if target == "zenith":
            # Set Orchis dark theme
            if shutil.which("dconf"):
                subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/gtk-theme", "'Orchis-Dark'"], check=False)
                subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/icon-theme", "'Reversal-dark'"], check=False)
                subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/color-scheme", "'prefer-dark'"], check=False)
            if shutil.which("gsettings"):
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Orchis-Dark"], check=False)
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", "Reversal-dark"], check=False)
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark"], check=False)

            time.sleep(0.5)
            self.start_shell()

            theme_sh = home / ".config/quickshell/scripts/zenith-theme.sh"
            if theme_sh.is_file() and os.access(theme_sh, os.X_OK):
                subprocess.run([str(theme_sh), "--current"], check=False, stderr=subprocess.DEVNULL)

        elif target == "caelestia":
            if shutil.which("dconf"):
                subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/icon-theme", "'Reversal-dark'"], check=False)
            if shutil.which("gsettings"):
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", "Reversal-dark"], check=False)

            caelestia_dir = home / ".config/caelestia"
            caelestia_dir.mkdir(parents=True, exist_ok=True)
            cli_json = caelestia_dir / "cli.json"
            if not cli_json.exists():
                cli_json.write_text('{\n  "theme": {\n    "iconTheme": "Reversal-dark",\n    "iconThemeDark": "Reversal-dark",\n    "iconThemeLight": "Reversal"\n  }\n}\n')

            if shutil.which("caelestia"):
                subprocess.run(["caelestia", "scheme", "set", "-n", "dynamic"], check=False, stderr=subprocess.DEVNULL)
                curr_wall = None
                p_txt = home / ".local/state/caelestia/wallpaper/path.txt"
                p_cur = home / ".current_wallpaper"
                if p_txt.exists():
                    curr_wall = p_txt.read_text().strip()
                elif p_cur.exists():
                    curr_wall = p_cur.read_text().strip()
                if curr_wall and Path(curr_wall).exists():
                    subprocess.run(["caelestia", "wallpaper", "-f", curr_wall], check=False, stderr=subprocess.DEVNULL)

            time.sleep(0.5)
            if shutil.which("caelestia-shell"):
                subprocess.Popen(["caelestia-shell", "-d"], start_new_session=True)
            else:
                warn("caelestia-shell binary not found in PATH")

        elif target == "end-4":
            if shutil.which("dconf"):
                subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/icon-theme", "'Reversal-dark'"], check=False)
            time.sleep(0.5)
            if shutil.which("end4-shell"):
                subprocess.Popen(["end4-shell", "-d"], start_new_session=True)
            else:
                subprocess.Popen(["quickshell", "-d"], start_new_session=True)

        if shutil.which("hyprctl"):
            subprocess.run(["hyprctl", "reload"], check=False, stderr=subprocess.DEVNULL)

        ok(f"switched to {target} shell")

    def print_ipc(self) -> None:
        if shutil.which("qs"):
            subprocess.run(["qs", "ipc"], check=False)
        else:
            step("quickshell IPC tools not found")

    def print_log(self) -> None:
        log_file = Path("/tmp/quickshell.log")
        if log_file.exists():
            print(log_file.read_text())
        else:
            warn("no /tmp/quickshell.log found")

    def call_ipc(self) -> None:
        msg = getattr(self.args, "message", [])
        if not msg:
            warn("no IPC message provided")
            return
        if shutil.which("qs"):
            subprocess.run(["qs", "ipc", "call", *msg], check=False)
        else:
            warn("qs not found in PATH")
