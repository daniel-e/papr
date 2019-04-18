import os
import termcolor


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


def print_header():
    cols, _ = os.get_terminal_size(0)
    print("Id    Title " + " " * (cols - 12 - 8) + "Stars" + "  ")
    _hr()
    return cols


def print_paper(paper, selected = False):
    cols, _ = os.get_terminal_size(0)
    # 5 columns for id
    # 1 columns for space
    # 2 columns at the end of the line for notes
    # n columns for filename

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

    m = "{:5d} {}".format(paper.idx(), f)
    s = colored("line", selected, m)
    if len(m) < cols:
        s = s + colored("line", selected, " " * (cols - len(m) - 2 - len_stars - len_tags))

    if len_tags > 0:
        s = s + colored("line", selected, " [") + colored("tags", selected, tags) + colored("line", selected, "]")
    if len_stars > 0:
        s = s + colored("line", selected, " [" + stars + "]")

    if paper.has_notes():
        s += colored("line", selected, " ✺")
    else:
        s += colored("line", selected, "  ")

    print(s)


def colored(typ, selected, s):
    mapping = {"line": "white", "tags": "green"}
    if selected:
        return termcolor.colored(s, mapping[typ], 'on_red', attrs=["bold"])
    else:
        return termcolor.colored(s, mapping[typ])


def print_papers(papers):
    for paper in papers:
        print_paper(paper)

