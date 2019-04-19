from .tools import show_pdf


def cmd_last(args, repo):
    p = -1
    if len(args) > 0:
        p = -int(args[0])
    r = repo.list()
    if len(r) == 0:
        print("empty")
        return
    show_pdf(r[p], repo.pdf_path())


