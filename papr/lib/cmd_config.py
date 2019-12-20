import sys

from .config import Config


def error():
    print("Possible keys:")
    print("viewer")
    sys.exit(1)

def cmd_config(args, conf):
    if len(args) != 2:
        print("You need to specify a key and a value.")
        error()
    key = args[0]
    val = args[1]
    if key == "viewer":
        conf.set_viewer(val)
        print("Set viewer to value:", val)
    else:
        print("Unknown key.")
        error()



