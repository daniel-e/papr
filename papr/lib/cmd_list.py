from .termout import print_header, print_papers
from .repository import Repository


def cmd_list(repo: Repository):
    r = repo.list()
    if len(r) == 0:
        print("empty")
    else:
        print_header()
        print_papers(r)


