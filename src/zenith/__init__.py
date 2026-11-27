from zenith.parser import parse_args
from zenith.utils.io import log

__version__ = "0.1.0"


def main() -> None:
    try:
        parser, args = parse_args()
        if args.version:
            print(f"zenith-cli v{__version__}")
        elif hasattr(args, "cls"):
            args.cls(args).run()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        log("\nExiting...")
