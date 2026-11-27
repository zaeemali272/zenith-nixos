import subprocess


def notify(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["notify-send", "-a", "zenith-cli", *args],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""


def close_notification(nid: str) -> None:
    subprocess.run(
        [
            "gdbus",
            "call",
            "--session",
            "--dest=org.freedesktop.Notifications",
            "--object-path=/org/freedesktop/Notifications",
            "--method=org.freedesktop.Notifications.CloseNotification",
            str(nid),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )
