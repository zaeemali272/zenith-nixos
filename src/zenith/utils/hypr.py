import json
import os
import socket
from typing import Any

socket_base = f"{os.getenv('XDG_RUNTIME_DIR', '')}/hypr/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE', '')}"
socket_path = f"{socket_base}/.socket.sock"
socket2_path = f"{socket_base}/.socket2.sock"

_lua_config_cache: bool | None = None


def message(msg: str, is_json: bool = True) -> Any:
    if not os.path.exists(socket_path):
        return {} if is_json else ""

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            sock.connect(socket_path)

            if is_json:
                msg = f"j/{msg}"
            sock.sendall(msg.encode())

            chunks: list[bytes] = []
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                chunks.append(chunk)
            resp = b"".join(chunks).decode(errors="replace")

            return json.loads(resp) if is_json else resp
    except Exception:
        return {} if is_json else ""


def is_lua_config() -> bool:
    global _lua_config_cache
    if _lua_config_cache is not None:
        return _lua_config_cache
    try:
        result = message("status")
        if isinstance(result, dict):
            _lua_config_cache = bool(result.get("configProvider") == "lua")
        else:
            _lua_config_cache = False
        return _lua_config_cache
    except Exception:
        _lua_config_cache = False
        return False


DISPATCHER_MAP_LUA = {
    "togglespecialworkspace": lambda *a: (
        f'hl.dsp.workspace.toggle_special("{a[0]}")' if a else "hl.dsp.workspace.toggle_special()"
    ),
    "movetoworkspacesilent": lambda *a: (
        f'hl.dsp.window.move({{window = "address:{a[0].split(",")[1].replace("address:", "")}", workspace = "{a[0].split(",")[0]}", follow = false}})'
    ),
    "exec": lambda *a: 'hl.dsp.exec_cmd("' + " ".join(a).replace("\\", "\\\\").replace('"', '\\"') + '")',
}


def dispatch(dispatcher: str, *args: str) -> bool:
    if is_lua_config() and dispatcher in DISPATCHER_MAP_LUA:
        lua_dispatch = DISPATCHER_MAP_LUA[dispatcher](*args)
        return message(f"dispatch {lua_dispatch}", is_json=False) == "ok"
    arg_str = " ".join(map(str, args)).rstrip()
    cmd = f"dispatch {dispatcher} {arg_str}".rstrip()
    return message(cmd, is_json=False) == "ok"


def monitors() -> list[dict[str, Any]]:
    res = message("monitors")
    return res if isinstance(res, list) else []


def clients() -> list[dict[str, Any]]:
    res = message("clients")
    return res if isinstance(res, list) else []


def workspaces() -> list[dict[str, Any]]:
    res = message("workspaces")
    return res if isinstance(res, list) else []
