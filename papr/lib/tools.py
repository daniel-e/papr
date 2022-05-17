import os
import re
import time
from pathlib import Path
from subprocess import Popen, DEVNULL

from .paper import Paper
from .edit import create_tmp_file
from .html import export_papers_html


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


def merge_overlaps(positions):
    if len(positions) < 2:
        return positions
    p = positions[:]
    p.sort()
    p_beg, p_end = p[0]
    r_beg, r_end = p[1]
    if r_beg < p_end:
        return merge_overlaps(p[2:] + [(p_beg, max(p_end, r_end))])
    else:
        return [p[0]] + merge_overlaps(p[1:])


def highlight_query(paper: Paper, query):
    positions = []
    for q in query.split():
        start_pos = 0
        while True:
            pos = paper.title().lower().find(q.lower(), start_pos)
            if pos == -1:
                break
            positions.append((pos, pos + len(q)))
            start_pos = pos + len(q)
    return merge_overlaps(positions)


def filter_list(papers, query):
    return [p for p in papers if substrings_exist_in(p, query) or len(query) == 0]


def filter_list_re(papers, query):
    return [p for p in papers if re_exists_in(p, query) or len(query) == 0]


def show_pdf(p: Paper, repo_path, path_viewer):
    try:
        Popen([path_viewer, repo_path + "/" + p.filename()], stderr=DEVNULL, stdout=DEVNULL)
    except:
        pass


def show_in_browser(repo, p: Paper, browser, browser_params=[]):
    tmp = create_tmp_file(ext="html")
    export_papers_html(repo, [p], tmp, with_pdf_link=True)
    try:
        # TODO configure browser
        Popen([browser] + browser_params + ["file://" + tmp], stderr=DEVNULL, stdout=DEVNULL)
    except:
        pass

