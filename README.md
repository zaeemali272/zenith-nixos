# ⚡ zenith-cli

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-FCC624.svg?style=for-the-badge&logo=linux&logoColor=black)](https://kernel.org)

**zenith-cli** is the unified command line interface and system orchestrator for the **Zenith** desktop environment. Modeled after modular Linux desktop tools, it provides a single, high-performance interface for shell management, Hyprland scratchpads, screenshotting, screen recording, and system maintenance across **NixOS** and **Arch Linux**.

---

## 🚀 Features

- **Desktop Shell Manager**: Switch seamlessly between `zenith-shell`, `caelestia-shell`, and `end-4`. Start, restart, and inspect shell state.
- **Hyprland Workspace Toggling**: Toggle special workspaces (`sysmon`, `communication`, `music`, `todo`) with intelligent auto-spawning.
- **Media Controls**: Region & fullscreen screenshots (`grim`, `slurp`, `swappy`), screen recording (`gpu-screen-recorder`, `wl-screenrec`), and wallpaper switching (`awww`).
- **Clipboard & Glyph Pickers**: Integrated Fuzzel dmenu interface for clipboard history and emojis/glyphs.
- **Dual-Distro System Operations**: Unified commands for rebuilding (`nh` / `nixos-rebuild` / `yay`), updates, generation rollback, garbage collection, and deep disk cleaning.
- **Self-Healing Diagnostics**: Built-in `zenith doctor` verifies hardware nodes, session agents, virtualisation, audio, and configuration integrity.

---

## 📦 Installation

### ❄️ Option 1: NixOS (Flake)

Add `zenith-cli` as an input in your system `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    zenith-cli = {
      url = "github:zaeemali272/zenith-cli";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, zenith-cli, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        {
          environment.systemPackages = [
            zenith-cli.packages.${pkgs.stdenv.hostPlatform.system}.default
          ];
        }
      ];
    };
  };
}
```

### 🏹 Option 2: Arch Linux & Other Distributions

#### Using Pip / Pipx:
```bash
git clone https://github.com/zaeemali272/zenith-cli.git ~/zenith/zenith-cli
cd ~/zenith/zenith-cli

# Install in editable or system mode
pip install --break-system-packages .
# Or with pipx:
pipx install .
```

#### Manual / Direct Symlink:
```bash
mkdir -p ~/.local/bin
ln -sf ~/zenith/zenith-cli/bin/zenith ~/.local/bin/zenith
```

---

## 🛠️ Command Reference

### System Maintenance

| Command | Description |
| :--- | :--- |
| `zenith doctor` | Run the 10-point health and diagnostic check across system components. |
| `zenith rebuild [switch\|boot\|test]` | Rebuild system (calls `nh os` / `nixos-rebuild` on NixOS; `yay` on Arch). |
| `zenith update` | Pull latest updates in configuration directory and trigger system rebuild. |
| `zenith rollback` | Boot the previous NixOS generation. |
| `zenith gc [days]` | Remove generations older than N days (default: 7) or clean package cache. |
| `zenith clean [days]` | 5-step deep disk cleaning: GC, temp files, thumbnails, journals, and store. |
| `zenith where` | Print active system configuration directory path. |

### Desktop Shell

| Command | Description |
| :--- | :--- |
| `zenith shell start` | Start the active desktop shell in the background. |
| `zenith shell restart` | Gracefully restart the currently active desktop shell. |
| `zenith shell switch <name>` | Switch between `zenith`, `caelestia`, and `end-4` (updates GTK/Qt/QML). |
| `zenith shell list` | List available desktop shells and display which one is active. |
| `zenith shell kill` | Terminate all active shell processes. |
| `zenith shell log` | Print the recent desktop shell log output. |

### Hyprland & Desktop Utilities

| Command | Description |
| :--- | :--- |
| `zenith toggle <workspace>` | Toggle scratchpads: `sysmon` (btop), `communication` (discord), `music` (spotify), `todo` (todoist). |
| `zenith screenshot` | Take a fullscreen screenshot (saved to cache and copied to clipboard). |
| `zenith screenshot -r` | Interactively select a region with slurp and open with swappy. |
| `zenith record` | Toggle screen recording via GPU Screen Recorder. |
| `zenith record -r -s` | Record a selected screen region with microphone/system audio. |
| `zenith wallpaper -f <path>` | Set new wallpaper via awww and trigger dynamic palette regeneration. |
| `zenith wallpaper -r [dir]` | Pick a random wallpaper from your wallpapers directory. |
| `zenith clipboard` | Open searchable clipboard history in Fuzzel. |
| `zenith clipboard -d` | Delete items from clipboard history. |
| `zenith emoji` | Open emoji and unicode symbol picker. |

---

## 🐚 Shell Completions

Fish shell completions are provided in `completions/zenith.fish`:
```bash
mkdir -p ~/.config/fish/completions
cp completions/zenith.fish ~/.config/fish/completions/
```

---

## 📜 License

Licensed under the [MIT License](LICENSE).
