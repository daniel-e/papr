from .termout import print_header, print_papers


def cmd_list(repo):
    r = repo.list()
    if len(r) == 0:
        print("empty")
    else:
        print_header()
        print_papers(r)


