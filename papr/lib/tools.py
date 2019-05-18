import re
from subprocess import Popen, DEVNULL

from .paper import Paper


VIEWER = "/usr/bin/evince"


def re_exists_in(p: Paper, q):
    try:
        r = re.compile(q.lower())
        if r.search(p.title().lower()):
            return True
        return False
    except Exception:
        return False


def substrings_exist_in(paper: Paper, query):
    for q in query.split():
        if paper.title().lower().find(q.lower()) < 0:
            return False
    return True


def filter_list(papers, query):
    return [p for p in papers if substrings_exist_in(p, query) or len(query) == 0]


def filter_list_re(papers, query):
    return [p for p in papers if re_exists_in(p, query) or len(query) == 0]


def show_pdf(p: Paper, repo_path):
    Popen([VIEWER, repo_path + "/" + p.filename()], stderr=DEVNULL, stdout=DEVNULL)


