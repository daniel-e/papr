import re
from subprocess import Popen, DEVNULL

from .paper import Paper


VIEWER = "/usr/bin/evince"


def exists_in(p, q):
    try:
        r = re.compile(q.lower())
        if r.search(p.title().lower()):
            return True
        return False
    except Exception:
        return False


def filter_list(l, query):
    return [i for i in l if exists_in(i, query)]


def show_pdf(p: Paper, repo_path):
    Popen([VIEWER, repo_path + "/" + p.filename()], stderr=DEVNULL, stdout=DEVNULL)


