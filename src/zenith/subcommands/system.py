from argparse import Namespace
import getpass
import os
from pathlib import Path
import platform
import re
import shutil
import socket
import subprocess

from zenith.utils.io import fatal, ok, step, warn
from zenith.utils.paths import find_config, get_home
from zenith.utils.system import is_arch, is_nixos


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        action = getattr(self.args, "system_action", None) or getattr(self.args, "subcommand", None)
        if not action:
            action = "doctor"

        if action == "update":
            self.update()
        elif action == "rebuild":
            self.rebuild()
        elif action == "rollback":
            self.rollback()
        elif action == "gc":
            self.gc()
        elif action == "clean":
            self.clean()
        elif action == "doctor":
            self.doctor()
        elif action == "where":
            self.where()
        else:
            fatal(f"unknown system command: {action}")

    def get_config_dir(self) -> Path:
        cfg = find_config()
        if not cfg:
            fatal("no configuration found. Set ZENITH_DIR to your config directory.")
        return cfg

    def where(self) -> None:
        cfg = self.get_config_dir()
        print(cfg)

    def rebuild(self) -> None:
        cfg = self.get_config_dir()
        host = socket.gethostname()
        target = getattr(self.args, "action_target", "switch") or "switch"

        if is_nixos():
            host_dir = cfg / "hosts" / host
            if not host_dir.is_dir():
                fatal(f"no hosts/{host} found in {cfg} -- see 'zenith doctor'")

            passthrough = getattr(self.args, "passthrough", []) or []

            if shutil.which("nh"):
                step(f"rebuilding {host} ({target}) via nh")
                cmd = ["nh", "os", target, f"{cfg}#{host}"]
                if passthrough:
                    cmd.extend(passthrough)
                subprocess.run(cmd, check=True)
            else:
                step(f"rebuilding {host} ({target}) via nixos-rebuild")
                cmd = ["sudo", "nixos-rebuild", target, "--flake", f"{cfg}#{host}"]
                if passthrough:
                    cmd.extend(passthrough)
                subprocess.run(cmd, check=True)
            ok("rebuild completed successfully")

        elif is_arch():
            step("updating system packages on Arch Linux...")
            if shutil.which("yay"):
                subprocess.run(["yay", "-Syu", "--noconfirm"], check=True)
            elif shutil.which("pacman"):
                subprocess.run(["sudo", "pacman", "-Syu", "--noconfirm"], check=True)
            ok("Arch Linux packages updated")
        else:
            step(f"system rebuild requested for {platform.system()}")

    def update(self) -> None:
        cfg = self.get_config_dir()
        step(f"pulling latest updates in {cfg}...")
        subprocess.run(["git", "-C", str(cfg), "pull", "--ff-only"], check=False)
        self.rebuild()

    def rollback(self) -> None:
        if is_nixos():
            step("rolling back to the previous NixOS generation")
            subprocess.run(["sudo", "nixos-rebuild", "switch", "--rollback"], check=True)
            ok("rollback completed")
        else:
            warn("rollback is currently only supported on NixOS")

    def _resolve_days(self) -> int:
        days_opt = getattr(self.args, "days_opt", None)
        if days_opt is not None:
            return days_opt
        days = getattr(self.args, "days", None)
        if days is not None:
            return days
        target = getattr(self.args, "action_target", None)
        if isinstance(target, str) and target != "switch":
            s = target.strip().lower()
            if s.endswith("d"):
                s = s[:-1]
            if s.isdigit():
                return int(s)
        return 7

    def gc(self) -> None:
        days = self._resolve_days()
        if is_nixos():
            step(f"removing NixOS generations older than {days}d")
            subprocess.run(["sudo", "nix-collect-garbage", "--delete-older-than", f"{days}d"], check=False)
            subprocess.run(["nix-collect-garbage", "--delete-older-than", f"{days}d"], check=False)
            ok("garbage collection completed")
        elif is_arch():
            step("cleaning package cache...")
            if shutil.which("paccache"):
                subprocess.run(["sudo", "paccache", "-r"], check=False)
            elif shutil.which("yay"):
                subprocess.run(["yay", "-Sc", "--noconfirm"], check=False)
            ok("cache cleaned")

    def clean(self) -> None:
        days = self._resolve_days()
        cfg = self.get_config_dir()

        step(f"1/5: running garbage collection (older than {days}d)")
        if is_nixos():
            subprocess.run(["sudo", "nix-collect-garbage", "--delete-older-than", f"{days}d"], check=False, stderr=subprocess.DEVNULL)
            subprocess.run(["nix-collect-garbage", "--delete-older-than", f"{days}d"], check=False, stderr=subprocess.DEVNULL)
        elif shutil.which("paccache"):
            subprocess.run(["sudo", "paccache", "-r"], check=False)
        ok("generations and packages cleaned")

        step("2/5: removing build artifacts and temp files")
        for res in cfg.glob("result*"):
            try:
                if res.is_symlink() or res.is_file():
                    res.unlink()
                elif res.is_dir():
                    shutil.rmtree(res)
            except OSError:
                pass
        ok("temp files purged")

        step("3/5: clearing user cache files and trash")
        home = get_home()
        for c in [home / ".cache/thumbnails", home / ".local/share/Trash"]:
            if c.exists():
                shutil.rmtree(c, ignore_errors=True)
        ok("caches and trash emptied")

        step("4/5: vacuuming systemd journal logs")
        if shutil.which("journalctl"):
            cmd = ["journalctl", "--vacuum-time=2d", "--vacuum-size=50M"]
            if os.geteuid() == 0:
                subprocess.run(cmd, check=False, stderr=subprocess.DEVNULL)
            elif shutil.which("sudo"):
                subprocess.run(["sudo", *cmd], check=False, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["journalctl", "--user", "--vacuum-time=2d", "--vacuum-size=50M"], check=False, stderr=subprocess.DEVNULL)
        ok("journal logs vacuumed")

        step("5/5: optimizing storage")
        if is_nixos():
            if os.geteuid() == 0:
                subprocess.run(["nix-store", "--optimise"], check=False)
            elif shutil.which("sudo"):
                subprocess.run(["sudo", "nix-store", "--optimise"], check=False)
        ok("storage optimized")

        step("disk space summary")
        subprocess.run(["df", "-h", "/"], check=False)
        ok("cleanup complete")

    def doctor(self) -> None:
        cfg = find_config()
        host = socket.gethostname()
        current_user = getpass.getuser()

        step("config")
        print(f"     directory: {cfg or 'Not found'}")
        print(f"     hostname:  {host}")
        if cfg and (cfg / "hosts" / host).is_dir():
            ok(f"hosts/{host} exists")
        elif is_nixos():
            warn(f"no hosts/{host} -- see zenith doctor for NixOS setup")

        step("identity")
        if cfg and (cfg / "vars.nix").is_file():
            content = (cfg / "vars.nix").read_text()
            m = re.search(r'user\s*=\s*"([^"]+)"', content)
            if m:
                configured_user = m.group(1)
                if configured_user == current_user:
                    ok(f"vars.nix user is {configured_user}")
                else:
                    warn(f"vars.nix says user = \"{configured_user}\" but you are {current_user}")
            else:
                warn("could not read user from vars.nix")
        else:
            ok(f"user: {current_user}")

        step("desktop session")
        res = subprocess.run(["pgrep", "-f", "polkitagent|polkit-gnome|polkit-kde"], capture_output=True, check=False)
        if res.returncode == 0:
            ok("a polkit agent is running")
        else:
            warn("no polkit agent -- privileged actions will fail silently")

        step("virtualisation")
        if shutil.which("virsh"):
            v_res = subprocess.run(["virsh", "-c", "qemu:///system", "net-info", "default"], capture_output=True, text=True, check=False)
            if "Active: yes" in v_res.stdout or "yes" in v_res.stdout:
                ok("libvirt default network is active")
            else:
                warn("libvirt default network is inactive -- VMs will refuse to start")

        step("battery care")
        charge_limit_writable = False
        candidates = list(Path("/sys/bus/platform/drivers/ideapad_acpi").glob("*/conservation_mode")) + \
                     list(Path("/sys/class/power_supply").glob("*/charge_control_end_threshold"))
        if candidates:
            node = candidates[0]
            if os.access(node, os.W_OK):
                ok("charge limit is writable without a password")
            else:
                warn("charge limit is read-only -- the desktop toggle needs a password prompt")

        step("audio subsystem")
        p_pw = subprocess.run(["pgrep", "-f", "pipewire"], capture_output=True, check=False)
        p_wp = subprocess.run(["pgrep", "-f", "wireplumber"], capture_output=True, check=False)
        if p_pw.returncode == 0 and p_wp.returncode == 0:
            ok("pipewire and wireplumber are active")
        else:
            warn("audio subsystem incomplete")

        step("graphics & display")
        if Path("/dev/dri").is_dir():
            ok("hardware rendering device nodes present (/dev/dri)")
        else:
            warn("no /dev/dri render devices detected")

        step("backlight permissions")
        bl_paths = list(Path("/sys/class/backlight").glob("*/brightness"))
        if bl_paths:
            all_w = all(os.access(p, os.W_OK) for p in bl_paths)
            if all_w:
                ok(f"backlight brightness nodes writable ({bl_paths[0].name})")
            else:
                warn(f"backlight node {bl_paths[0]} is not writable by current user")

        step("desktop shell & daemons")
        p_qs = subprocess.run(["pgrep", "-f", "quickshell|caelestia-shell"], capture_output=True, check=False)
        if p_qs.returncode == 0:
            ok("desktop shell is running")
        else:
            warn("desktop shell is not currently running")

        if shutil.which("awww"):
            a_res = subprocess.run(["awww", "query"], capture_output=True, check=False)
            if a_res.returncode == 0:
                ok("awww wallpaper daemon is active")
            else:
                warn("awww-daemon is not running")

        if is_nixos():
            step("store")
            gen = subprocess.run(
                ["nix-env", "--list-generations", "-p", "/nix/var/nix/profiles/system"],
                capture_output=True,
                text=True,
                check=False
            )
            count = len(gen.stdout.strip().splitlines()) if gen.stdout.strip() else 0
            if count > 0:
                print(f"     {count} system generations")
            ok("nix store accessible")
