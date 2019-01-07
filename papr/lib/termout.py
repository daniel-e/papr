import os
import termcolor


def _hr():
    cols, _ = os.get_terminal_size(0)
    print("─" * cols)


def rows():
    _, rows = os.get_terminal_size(0)
    return rows


def empty_line():
    cols, _ = os.get_terminal_size(0)
    return " " * cols


def print_header():
    cols, _ = os.get_terminal_size(0)
    print("Id    Title " + " " * (cols - 12))
    _hr()
    return cols


def print_paper(paper, selected = False):
    cols, _ = os.get_terminal_size(0)
    # 5 columns for id
    # 1 columns for space
    # 2 columns at the end of the line for notes
    # cols - (5 + 1 + 2) columns for filename
    n = cols - (5 + 1 + 2)
    f = paper.title()
    if len(f) > n:
        f = f[:n - 3] + "..."
    s = "{:5d} {}".format(paper.idx(), f)
    if len(s) < cols:
        s = s + (" " * (cols - len(s) - 2))
        if paper.has_notes():
            s += " ✺"
        else:
            s += "  "
    if selected:
        print(termcolor.colored(s, 'white', 'on_red', attrs=["bold"]))
    else:
        print(termcolor.colored(s, 'white'))


def print_papers(papers):
    for paper in papers:
        print_paper(paper)

