import os
from pathlib import Path


def get_home() -> Path:
    return Path.home()


def find_config() -> Path | None:
    # 1. Respect explicit environment variable
    if os.getenv("ZENITH_DIR"):
        p = Path(os.getenv("ZENITH_DIR")).expanduser().resolve()
        if (p / "flake.nix").exists() or (p / "install.sh").exists():
            return p

    home = get_home()
    # 2. Check canonical paths - prefer repos with flake.nix if on NixOS
    candidates = [
        home / "zenith",
        home / "zenith" / "zenith",
        home / "zenith" / "zenith-nixos",
        home / ".config" / "zenith",
        Path("/etc/nixos"),
    ]

    # First pass: find candidate with flake.nix
    for candidate in candidates:
        if (candidate / "flake.nix").is_file():
            return candidate

    # Second pass: find candidate with install.sh
    for candidate in candidates:
        if (candidate / "install.sh").is_file():
            return candidate

    return None


zenith_config_dir = get_home() / ".config" / "zenith"
active_shell_path = zenith_config_dir / "active-shell"

cache_dir = Path(os.getenv("XDG_CACHE_HOME", get_home() / ".cache")) / "zenith"
state_dir = Path(os.getenv("XDG_STATE_HOME", get_home() / ".local" / "state")) / "zenith"

screenshots_dir = get_home() / "Pictures" / "Screenshots"
recordings_dir = get_home() / "Videos" / "Recordings"
wallpapers_dir = get_home() / "Pictures" / "Wallpapers"
current_wallpaper_file = get_home() / ".current_wallpaper"

recording_pid_path = cache_dir / "recording.pid"
recording_path_file = cache_dir / "recording.path"
