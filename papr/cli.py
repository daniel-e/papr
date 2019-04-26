#!/usr/bin/env python3

# Settings -> Project: papr -> Project Structure
#   use only papr as "Sources"

import sys

from .lib.cmd_default import cmd_default
from .lib.cmd_init import cmd_init
from .lib.cmd_last import cmd_last
from .lib.cmd_list import cmd_list
from .lib.cmd_read import cmd_read
from .lib.cmd_search import cmd_search
from .lib.ui import run_ui
from .lib.config import Config
from .lib.repository import Repository
from .lib.help import help
from .lib.cmd_add import cmd_add
from .lib.cmd_fetch import cmd_fetch


def parse_command(conf: Config, repo: Repository) -> None:
    if len(sys.argv) > 1:
        c = sys.argv[1]
        if c == "init":
            cmd_init(repo)
            return
        elif c == "help" or c == "--help" or c == "-h":
            help(0)
        elif c == "default":
            cmd_default(conf, repo)
            return

    # For all other commands we need a valid repository.
    if not repo.is_valid():
        print("No repository.")
        sys.exit(1)

    # no arguments given -> show UI
    if len(sys.argv) < 2:
        run_ui(sys.argv[2:], repo)
        sys.exit(0)

    c = sys.argv[1]
    if c == "list":
        cmd_list(repo)
    elif c == "fetch":
        cmd_fetch(sys.argv[2:], repo)
    elif c == "read":
        cmd_read(sys.argv[2:], repo)
    elif c == "search":
        cmd_search(sys.argv[2:], repo)
    elif c == "last":
        cmd_last(sys.argv[2:], repo)
    elif c == "add":
        cmd_add(sys.argv[2:], repo)
    else:
        help(1)


def main() -> None:
    # Reads the configuration from "~/.papr/". Creates a default config if
    # it doesn't exist yet.
    conf = Config()
    # If we are in a repository create an instance of this repository. If we
    # are not in a repository create an instance of the default repository. If
    # there is no default repository, Repository.is_valid() will return False.
    r = Repository(conf)
    parse_command(conf, r)


if __name__ == "__main__":
    main()
