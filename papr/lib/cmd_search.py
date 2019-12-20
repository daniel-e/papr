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
    query = args[0]
    r = filter_list(r, query)
    if len(r) == 0:
        print("Not found.")
    else:
        print_papers(r)


