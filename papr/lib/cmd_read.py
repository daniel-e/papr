import sys

from .tools import show_pdf


def cmd_read(args, repo):
    if len(args) == 0:
        print("You need to specify a paper id.")
        sys.exit(1)
    p = repo.get_paper(int(args[0]))
    if not p:
        print("Not found.")
        sys.exit(1)
    show_pdf(p, repo.pdf_path())


