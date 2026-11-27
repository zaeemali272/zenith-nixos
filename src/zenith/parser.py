import argparse
import sys

from zenith.subcommands import (
    clipboard,
    emoji,
    record,
    resizer,
    scheme,
    screenshot,
    shell,
    system,
    toggle,
    wallpaper,
)


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="zenith",
        description="Unified CLI for Zenith dotfiles and desktop system management"
    )
    parser.add_argument("-v", "--version", action="store_true", help="print version")

    command_parser = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="COMMAND",
        help="the command to run"
    )

    # --- shell ---
    shell_parser = command_parser.add_parser("shell", help="start, restart, or switch desktop shell")
    shell_parser.set_defaults(cls=shell.Command)
    shell_parser.add_argument("action", nargs="?", choices=["start", "restart", "switch", "use", "list", "ls", "kill", "show", "log", "call"], help="shell action")
    shell_parser.add_argument("target", nargs="?", help="target shell (for switch: zenith, caelestia, end-4)")
    shell_parser.add_argument("message", nargs="*", help="optional IPC arguments")
    shell_parser.add_argument("-d", "--daemon", action="store_true", help="start detached")
    shell_parser.add_argument("-r", "--restart", action="store_true", help="restart shell")
    shell_parser.add_argument("-k", "--kill", action="store_true", help="kill running shell instances")
    shell_parser.add_argument("-s", "--show", action="store_true", help="show IPC info")
    shell_parser.add_argument("-l", "--log", action="store_true", help="show shell log")

    # --- toggle ---
    toggle_parser = command_parser.add_parser("toggle", help="toggle a special workspace (sysmon, communication, music, todo)")
    toggle_parser.set_defaults(cls=toggle.Command)
    toggle_parser.add_argument("workspace", help="the workspace to toggle")

    # --- screenshot ---
    screenshot_parser = command_parser.add_parser("screenshot", help="capture a fullscreen or region screenshot")
    screenshot_parser.set_defaults(cls=screenshot.Command)
    screenshot_parser.add_argument("-r", "--region", action="store_true", help="select a region")
    screenshot_parser.add_argument("-f", "--freeze", action="store_true", help="freeze screen while selecting")

    # --- record ---
    record_parser = command_parser.add_parser("record", help="toggle screen recording")
    record_parser.set_defaults(cls=record.Command)
    record_parser.add_argument("-r", "--region", action="store_true", help="record a region")
    record_parser.add_argument("-s", "--sound", action="store_true", help="record audio")
    record_parser.add_argument("-p", "--pause", action="store_true", help="toggle pause state")

    # --- clipboard ---
    clipboard_parser = command_parser.add_parser("clipboard", help="open clipboard history picker")
    clipboard_parser.set_defaults(cls=clipboard.Command)
    clipboard_parser.add_argument("-d", "--delete", action="store_true", help="delete mode")

    # --- emoji ---
    emoji_parser = command_parser.add_parser("emoji", help="open emoji/glyph picker")
    emoji_parser.set_defaults(cls=emoji.Command)

    # --- wallpaper ---
    wallpaper_parser = command_parser.add_parser("wallpaper", help="manage active wallpaper")
    wallpaper_parser.set_defaults(cls=wallpaper.Command)
    wallpaper_parser.add_argument("-f", "--file", help="path to wallpaper image")
    wallpaper_parser.add_argument("-r", "--random", nargs="?", const=True, help="pick a random wallpaper")
    wallpaper_parser.add_argument("-p", "--print", action="store_true", help="print current wallpaper")

    # --- scheme ---
    scheme_parser = command_parser.add_parser("scheme", help="manage color schemes")
    scheme_parser.set_defaults(cls=scheme.Command)
    scheme_parser.add_argument("scheme_action", nargs="?", choices=["list", "get", "set"], default="get")
    scheme_parser.add_argument("name", nargs="?", help="scheme name")

    # --- resizer ---
    resizer_parser = command_parser.add_parser("resizer", help="window resizer utility")
    resizer_parser.set_defaults(cls=resizer.Command)
    resizer_parser.add_argument("pattern", nargs="?", help="resizer mode ('pip' or width)")
    resizer_parser.add_argument("width", nargs="?", help="width")
    resizer_parser.add_argument("height", nargs="?", help="height")

    # --- system (explicit subcommand) ---
    sys_parser = command_parser.add_parser("system", help="system management commands")
    sys_parser.set_defaults(cls=system.Command)
    sys_parser.add_argument("system_action", choices=["update", "rebuild", "rollback", "gc", "clean", "doctor", "where"])
    sys_parser.add_argument("action_target", nargs="?", default="switch")
    sys_parser.add_argument("--days", type=int, default=7)
    sys_parser.add_argument("passthrough", nargs="*", help="extra arguments passed through to rebuild")

    # --- top-level system aliases for direct convenience & backwards-compatibility ---
    rebuild_p = command_parser.add_parser("rebuild", help="rebuild system configuration (switch|boot|test)")
    rebuild_p.set_defaults(cls=system.Command, system_action="rebuild")
    rebuild_p.add_argument("action_target", nargs="?", default="switch")
    rebuild_p.add_argument("passthrough", nargs="*")

    update_p = command_parser.add_parser("update", help="pull latest git updates and rebuild")
    update_p.set_defaults(cls=system.Command, system_action="update")
    update_p.add_argument("action_target", nargs="?", default="switch")
    update_p.add_argument("passthrough", nargs="*")

    rollback_p = command_parser.add_parser("rollback", help="boot previous generation")
    rollback_p.set_defaults(cls=system.Command, system_action="rollback")

    gc_p = command_parser.add_parser("gc", help="garbage collect old generations")
    gc_p.set_defaults(cls=system.Command, system_action="gc")
    gc_p.add_argument("days", nargs="?", type=int, default=7)

    clean_p = command_parser.add_parser("clean", help="deep system cleanup (temp, logs, gc, store)")
    clean_p.set_defaults(cls=system.Command, system_action="clean")
    clean_p.add_argument("days", nargs="?", type=int, default=7)

    doctor_p = command_parser.add_parser("doctor", help="check and verify system components")
    doctor_p.set_defaults(cls=system.Command, system_action="doctor")

    where_p = command_parser.add_parser("where", help="print active config directory")
    where_p.set_defaults(cls=system.Command, system_action="where")

    return parser, parser.parse_args()
