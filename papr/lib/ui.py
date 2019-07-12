import sys
import termcolor

from .console import cursor_on, cursor_off, cursor_top_left, cursor_up, cursor_down
from .edit import notes_of_paper, tags_of_paper, abstract_of_paper, details_of_paper, list_of_tags
from .termin import read_key
from .termout import rows, empty_line, print_paper, cols, write
from .tools import filter_list, show_pdf, filter_list_re
from .cmd_fetch import NEWTAG
from .ui_scrollview import ScrollView
from .repository import Repository


def expand_to_colwidth(s: str):
    c = cols()
    return s + (" " * (c - len(s)))


def hr():
    return "─" * cols()


def build_header():
    return "Id    Title " + " " * (cols() - 12 - 8) + "Stars" + "   " + hr()


def colored(s, fg, bg, bold=False):
    attr = ["bold"] if bold else []
    return termcolor.colored(s, fg, bg, attrs=attr)


def build_default_header():
    return termcolor.colored(
        expand_to_colwidth("ESC/q: quit | ENTER: open | ↑: up | ↓: down | s: search | n: notes | h: help"),
        "white", attrs=["bold"])


def build_search_header():
    return termcolor.colored(
        expand_to_colwidth("ESC: cancel + back to selection mode | ENTER: back to selection mode"),
        "white", "on_yellow", attrs=["bold"])


def build_title():
    return termcolor.colored(
        expand_to_colwidth("papr 0.0.16"),
        "white", "on_blue", attrs=["bold"])


def extent(s, width):
    return s + (" " * (width - len(s)))


def write_box(content, select_lineno=None, wmax=None, arrow_down=False, arrow_up=False):
    if not wmax:
        wmax = max([len(c) for c in content])
    write(colored("\r┌" + ("─" * wmax) + "┐", "white", "on_blue"))
    for idx, s in enumerate(content):
        cursor_down(1)
        write(colored("\r│", "white", "on_blue"))
        if idx == select_lineno:
            write(colored(extent(s, wmax), "white", "on_red", True))
        else:
            write(colored(extent(s, wmax), "white", "on_blue"))
        if arrow_up and idx == 0:
            write(colored("↑", "blue", "on_white"))
        elif arrow_down and idx == len(content) - 1:
            write(colored("↓", "blue", "on_white"))
        else:
            write(colored("│", "white", "on_blue"))
    cursor_down(1)
    write(colored("\r└" + ("─" * wmax) + "┘", "white", "on_blue"))


def redraw(state, papers, v):
    cursor_top_left()
    write(build_title())

    if state.in_search or state.in_re_search:
        write(build_search_header())
    else:
        write(build_default_header())
    write(build_header())

    cnt = 0 + 3
    for idx, p in enumerate(papers[v.first():v.end()]):
        print_paper(p, idx + v.first() == v.selected())
        cnt += 1

    # clear remaining lines
    n_rows = rows()
    while cnt < n_rows - 2:
        cnt += 1
        write(empty_line())

    # Now, the cursor is on the last line. Clear that line and go to the first column.
    sys.stdout.write(empty_line() + "\r")

    if state.in_search or state.in_re_search:
        write("Search: " + state.search + "▃")
    elif state.in_filter:
        if state.select_tag:
            write("Select a tag.")
            wmax = max([len(tag) for tag, _ in state.tags])
            tags = [extent(tag, wmax) for tag, _ in state.tags[state.tag_scrollview.first():state.tag_scrollview.end()]]
            cursor_up(2+state.tag_scrollview.rows())
            write_box(tags, state.tag_scrollview.selected() - state.tag_scrollview.first())
        else:
            write("Filter by: (t)ags")
    elif state.in_help:
        h = [
            " Key bindings",
            " ",
            " q / ESC       : Quit",
            " ENTER         : open the paper in a PDF reader.",
            " a             : Show abstract for paper.",
            " i / Arrow up  : Move selection up.",
            " k / Arrow down: Move selection down.",
            " s             : Live search in title.",
            " r             : Live search in title via regular expression. ",
            " n             : Edit notes.",
            " t             : Edit tags.",
            " 0..5          : Set voting.",
            " y             : Show all stored information about a paper.",
            " l             : Show statistics about tags.",
            " f             : Filter (e.g. by tags).",
            " F             : Clear filter."
        ]
        n = min(len(h), n_rows-2-1)   # number of lines in the box
        offset = state.in_help_offset # index of element in h which should be the first line in the box
        offset = min(offset, len(h)-n)
        state.in_help_offset = offset
        cursor_up(2+n)                # 2 lines for frame + n lines for text
        width = max([len(c) for c in h])
        arr_up = offset > 0
        arr_down = offset < len(h) - n
        write_box(h[offset:offset+n], wmax=width, arrow_down=arr_down, arrow_up=arr_up)
    else:
        if len(state.selected_tag) > 0:
            write("Tag: " + state.selected_tag)
        if len(state.selected_tag) > 0 and len(state.search) > 0:
            write(" | ")
        if len(state.search) > 0:
            write("Search: " + state.search)


class State:
    def __init__(self):
        self.search = ""
        self.in_search = False
        self.in_re_search = False

        self.in_filter = False
        self.select_tag = False
        self.tag_scrollview = None
        self.tags = []
        self.selected_tag = ""

        self.in_help = False
        self.in_help_offset = 0


def ui_main_or_search_loop(r, repo: Repository):
    n_papers = len(r)
    n_view_rows = rows() - 3 - 1 - 1
    # -3 = 3 rows for header
    # -1 = 1 row for search line
    # -1 = 1 "papr" header line
    v = ScrollView(n_elements=n_papers, rows=n_view_rows, selected=n_papers-1)

    s = State()
    papers = r[:]

    while True:
        cursor_off()
        redraw(s, papers, v)

        k = read_key()
        if k is None or k == '~':
            continue

        if s.in_search or s.in_re_search:
            f = filter_list_re if s.in_re_search else filter_list

            if ord(k) == 27:
                s.in_search = s.in_re_search = False
                s.search = ""
            elif ord(k) == 10:
                s.in_search = s.in_re_search = False
            elif ord(k) == 127:
                s.search = s.search[:-1]
            else:
                s.search += k

            papers = f(r, s.search)
            if len(s.selected_tag) > 0:
                papers = [p for p in papers if s.selected_tag in p.tags()]
            v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=len(papers)-1)
        elif s.in_filter:
            if s.select_tag:
                if ord(k) == 27:
                    s.in_filter = s.select_tag = False
                elif k == '#':
                    s.tag_scrollview.up()
                elif k == '+':
                    s.tag_scrollview.down()
                elif ord(k) == 10:
                    s.selected_tag = s.tags[s.tag_scrollview.selected()][0]
                    papers = [p for p in r if s.selected_tag in p.tags()]
                    v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=len(papers) - 1)
                    s.in_filter = False
            else:
                if k == 't':
                    s.select_tag = True
                    s.tags = repo.all_tags()
                    n = len(s.tags)
                    s.tag_scrollview = ScrollView(n_elements=n, rows=min(n_view_rows-2, n), selected=n-1)
                else:
                    s.in_filter = False
        elif s.in_help:
            if k == '#':
                s.in_help_offset = max(0, s.in_help_offset - 1)
            elif k == '+':
                s.in_help_offset += 1
            else:
                s.in_help = False
        else:
            if k == 'l':
                list_of_tags(repo)
            elif k == 'a':
                abstract_of_paper(papers[v.selected()])
            elif k == 'y':
                details_of_paper(papers[v.selected()])
            elif k == 'i' or k == '#':
                v.up()
            elif k == 'k' or k == '+':
                v.down()
            elif k == 'n':
                notes_of_paper(repo, papers[v.selected()])
            elif k == 't':
                tags_of_paper(repo, papers[v.selected()])
            elif ord(k) == 10:
                p = v.selected()
                papers[p].remove_tag(NEWTAG)
                repo.update_paper(papers[p])
                show_pdf(papers[p], repo.pdf_path())
            elif ord(k) == 27 or k == 'q':
                break
            elif k == 's':
                s.in_search = True
            elif k == 'r':
                s.in_re_search = True
            elif '0' <= k <= '5':
                stars = int(k)
                papers[v.selected()].set_stars(stars)
                repo.update_paper(papers[v.selected()])
            elif k == 'f':
                s.in_filter = True
                s.select_tag = False
            elif k == 'F':
                s.selected_tag = ""
                papers = r[:]
                v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=len(papers) - 1)
                # TODO: consider search
            elif k == 'h':
                s.in_help = True


def run_ui(args, repo: Repository):
    r = repo.list()
    if len(r) == 0:
        print("Repository is empty.")
        sys.exit(0)

    if len(args) > 0:
        r = filter_list(r, args[0])

    ui_main_or_search_loop(r, repo)
    cursor_on()
    print()


