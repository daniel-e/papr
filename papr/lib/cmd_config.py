import sys

from .config import Config

VALID_KEYS = ["viewer", "browser", "browser_params"]


def error():
    print("Possible keys:")
    print(", ".join(VALID_KEYS))
    sys.exit(1)


def cmd_config(args, conf: Config):
    if len(args) < 2:
        print("You need to specify a key and a value.")
        error()

    key = args[0]
    if key not in VALID_KEYS:
        print("You specified an invalid config key.")
        error()

    val = args[1].strip()
    if key == "viewer":
        conf.set_viewer(val)
        print("Set viewer to value:", val)
    elif key == "browser":
        conf.set_browser(val)
        print("Set browser to value:", val)
    elif key == "browser_params":
        conf.set_browser_params(args[1:])
        print("Set browser parameters to:", args[1:])
    else:
        print("Unknown key.")
        error()



