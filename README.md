# zenith-cli

The unified system and desktop control CLI for Zenith.

## Features

- **Desktop Shell Management**: Switch, start, restart, and inspect desktop shells (`zenith`, `caelestia`, `end-4`).
- **Hyprland Workspaces**: Toggle special workspaces for monitoring (`sysmon`), communication, music, and tasks.
- **Media Controls**: Screen recording (`record`), screenshots (`screenshot`), and wallpaper switching (`wallpaper`).
- **System Maintenance**: Dual-distro commands (`rebuild`, `update`, `rollback`, `gc`, `clean`, `doctor`, `where`) supporting NixOS and Arch Linux.

## Installation

### NixOS (Flake)
```nix
inputs.zenith-cli.url = "github:zaeemali272/zenith-cli";
```

### Python Package
```bash
pip install .
```

## Usage

```bash
zenith --help
zenith doctor
zenith shell switch zenith
zenith toggle sysmon
```
