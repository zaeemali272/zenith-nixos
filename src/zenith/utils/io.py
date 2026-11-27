import sys

BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
OFF = "\033[0m"


def step(msg: str) -> None:
    print(f"{BLUE}==>{OFF} {msg}")


def ok(msg: str) -> None:
    print(f"{GREEN}  ok{OFF} {msg}")


def warn(msg: str, prefix: bool = True) -> None:
    p = f"{YELLOW}  !!{OFF} " if prefix else ""
    print(f"{p}{msg}", file=sys.stderr)


def fatal(msg: str) -> None:
    print(f"{RED} error{OFF} {msg}", file=sys.stderr)
    sys.exit(1)


def log(msg: str) -> None:
    print(msg)
