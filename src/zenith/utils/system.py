import os
from pathlib import Path
import shutil
import subprocess
from typing import Sequence


def is_nixos() -> bool:
    return Path("/etc/NIXOS").exists() or shutil.which("nixos-rebuild") is not None


def is_arch() -> bool:
    return Path("/etc/arch-release").exists() or shutil.which("pacman") is not None


def get_distro_id() -> str:
    if Path("/etc/os-release").exists():
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.strip().split("=")[1].strip('"').lower()
        except Exception:
            pass
    if is_nixos():
        return "nixos"
    if is_arch():
        return "arch"
    return "linux"


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def run_command(
    cmd: Sequence[str] | str,
    check: bool = True,
    shell: bool = False,
    capture: bool = False,
    env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    custom_env = os.environ.copy()
    if env:
        custom_env.update(env)

    return subprocess.run(
        cmd,
        check=check,
        shell=shell,
        capture_output=capture,
        text=True,
        env=custom_env
    )
