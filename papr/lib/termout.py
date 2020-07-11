import os
import sys

import termcolor


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def _hr():
    cols, _ = os.get_terminal_size(0)
    print("─" * cols)


def rows():
    _, rows = os.get_terminal_size(0)
    return rows


def cols():
    cols, _ = os.get_terminal_size(0)
    return cols


def empty_line():
    cols, _ = os.get_terminal_size(0)
    return " " * cols


# TODO duplicate
def print_header():
    cols, _ = os.get_terminal_size(0)
    print("Id    Title " + " " * (cols - 12 - 8) + "Stars" + "  ")
    _hr()
    return cols


def print_paper(paper, selected=False):
    print(paper_line(paper, selected))


def paper_line(paper, selected=False):
    cols, _ = os.get_terminal_size(0)
    # 5 columns for id
    # 1 columns for space
    # 2 columns at the end of the line for notes
    # n columns for title

    stars = ""
    if paper.stars() >= 0:
        stars = " " * (5 - paper.stars()) + "*" * paper.stars()
    len_stars = len(stars) + 3

    tags = ""
    len_tags = 0
    if len(paper.tags()) > 0:
        tags = ",".join(paper.tags())
        len_tags = len(tags) + 3

    n = cols - (5 + 1 + 2) - len_stars - len_tags
    f = paper.title()
    if len(f) > n:
        f = f[:n - 3] + "..."

    orig_f = f

    h = paper.highlights()[:]
    h.sort(reverse=True)
    for beg, end in h:
        if beg < len(f):
            f = f[:beg] + colored("highlight", True, f[beg:end]) + colored("line", selected, f[end:])

    m = "{:5d} ".format(paper.idx())
    s = colored("line", selected, m + f)
    if len(m) + len(orig_f) < cols:
        s = s + colored("line", selected, " " * (cols - len(m + orig_f) - 2 - len_stars - len_tags))

    if len_tags > 0:
        s = s + colored("line", selected, " [") + colored("tags", selected, tags) + colored("line", selected, "]")
    if len_stars > 0:
        s = s + colored("line", selected, " [" + stars + "]")

    if paper.has_notes():
        s += colored("line", selected, " ✺")
    else:
        s += colored("line", selected, "  ")

    return s


def colored(typ, selected, s):
    mapping = {"line": "white", "tags": "green"}
    if typ == "highlight":
        return termcolor.colored(s, "yellow", 'on_yellow', attrs=["bold"])

    if selected:
        return termcolor.colored(s, mapping[typ], 'on_red', attrs=["bold"])
    else:
        return termcolor.colored(s, mapping[typ])


def print_papers(papers):
    for paper in papers:
        print_paper(paper)

