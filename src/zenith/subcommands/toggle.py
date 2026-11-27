from argparse import Namespace
import shutil
import subprocess

from zenith.utils import hypr
from zenith.utils.io import fatal, ok, step


WORKSPACE_DEFINITIONS = {
    "sysmon": {
        "workspace": "special:sysmon",
        "matches": [{"class": "btop"}, {"title": "btop"}],
        "command": ["kitty", "--class", "btop", "-T", "btop", "-e", "btop"],
    },
    "communication": {
        "workspace": "special:communication",
        "matches": [{"class": "discord"}, {"class": "vesktop"}, {"class": "whatsapp"}],
        "command": ["discord"],
    },
    "music": {
        "workspace": "special:music",
        "matches": [{"class": "Spotify"}, {"initialTitle": "Spotify"}, {"class": "feishin"}],
        "command": ["spotify"],
    },
    "todo": {
        "workspace": "special:todo",
        "matches": [{"class": "Todoist"}],
        "command": ["todoist"],
    },
}


class Command:
    args: Namespace

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        name = getattr(self.args, "workspace", None)
        if not name:
            fatal("workspace argument required (e.g. sysmon, communication, music, todo)")

        definition = WORKSPACE_DEFINITIONS.get(name)
        if not definition:
            # Direct toggle special workspace if not predefined
            target_ws = f"special:{name}" if not name.startswith("special:") else name
            hypr.dispatch("togglespecialworkspace", target_ws.replace("special:", ""))
            return

        target_ws = definition["workspace"].replace("special:", "")
        clients = hypr.clients()

        # Check if matching window exists
        matching_window = None
        for client in clients:
            c_class = client.get("class", "").lower()
            c_title = client.get("title", "").lower()
            for m in definition["matches"]:
                m_class = m.get("class", "").lower()
                m_title = m.get("title", "").lower()
                if (m_class and m_class in c_class) or (m_title and m_title in c_title):
                    matching_window = client
                    break
            if matching_window:
                break

        if matching_window:
            # Client exists, toggle the special workspace
            hypr.dispatch("togglespecialworkspace", target_ws)
        else:
            # Client is not running, spawn it
            cmd = definition["command"]
            bin_name = cmd[0]
            if shutil.which(bin_name):
                step(f"launching {bin_name} into {definition['workspace']}...")
                subprocess.Popen(cmd, start_new_session=True)
                # Toggle special workspace so it's open when the window appears
                hypr.dispatch("togglespecialworkspace", target_ws)
            else:
                fatal(f"command not found: {bin_name}")
