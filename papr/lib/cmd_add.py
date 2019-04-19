import sys
from .repository import Repository
from .paper import Paper


def cmd_add(args, repo: Repository):
    if len(args) == 0:
        print("You need to specify a filename.")
        sys.exit(1)
    filename = args[0]
    idx = repo.next_id()
    if len(args) > 1:
        idx = int(args[1])
    title = filename
    if title.rfind(".") >= 0:
        title = title[:title.rfind(".")]
    p = Paper(idx=idx, filename=filename, title=title)
    repo.add_paper(p)
    print("Added paper.")
    print("Filename:", filename)
