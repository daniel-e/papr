import sys

from .repository import Repository
from .termout import print_papers
from .tools import filter_list


def cmd_search(args, repo: Repository):
    if len(args) == 0:
        print("You need to specify a query.")
        sys.exit(1)
    r = repo.list()
    if len(r) == 0:
        print("empty")
        return
    r = filter_list(r, args[0])
    if len(r) == 0:
        print("Not found.")
    else:
        print_papers(r)


