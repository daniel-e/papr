import sys
import termcolor

from .console import cursor_on, cursor_off, cursor_top_left
from .edit import notes_of_paper, tags_of_paper, abstract_of_paper, details_of_paper, list_of_tags
from .termin import read_key
from .termout import rows, empty_line, print_paper, cols, write
from .tools import filter_list, show_pdf, filter_list_re
from .cmd_fetch import NEWTAG
from .ui_scrollview import ScrollView


def expand_to_colwidth(s: str):
    c = cols()
    return s + (" " * (c - len(s)))


def hr():
    return "─" * cols()


def build_header():
    return "Id    Title " + " " * (cols() - 12 - 8) + "Stars" + "   " + hr()


def build_default_header():
    return termcolor.colored(
        expand_to_colwidth("ESC/q: quit | ENTER: open | ↑: up | ↓: down | s: search | n: notes | t: tags"),
        "white", attrs=["bold"])


def build_search_header():
    return termcolor.colored(
        expand_to_colwidth("ESC: cancel + back to selection mode | ENTER: back to selection mode"),
        "white", "on_yellow", attrs=["bold"])


def build_title():
    return termcolor.colored(
        expand_to_colwidth("papr"),
        "white", "on_blue", attrs=["bold"])


def redraw(in_search, in_re_search, papers, v, search):
    cursor_top_left()
    write(build_title())

    if in_search or in_re_search:
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

    # search line
    sys.stdout.write(empty_line() + "\r")
    if in_search or in_re_search:
        write("search: " + search + "▃")
    elif len(search) > 0:
        write("search: " + search)


def ui_main_or_search_loop(r, repo):
    n_papers = len(r)
    n_view_rows = rows() - 3 - 1 - 1
    # -3 = 3 rows for header
    # -1 = 1 row for search line
    # -1 = 1 "papr" header line
    v = ScrollView(n_elements=n_papers, rows=n_view_rows, selected=n_papers-1)

    search = ""
    in_search = False
    in_re_search = False
    papers = r[:]

    while True:
        redraw(in_search, in_re_search, papers, v, search)

        k = read_key()
        if k is None or k == '~':
            continue

        if in_search or in_re_search:
            update_search = False
            if ord(k) == 27:
                in_search = in_re_search = False
                search = ""
                update_search = True
            elif ord(k) == 10:
                in_search = in_re_search = False
            elif ord(k) == 127:
                search = search[:-1]
                update_search = True
            else:
                search += k
                update_search = True

            if update_search:
                if len(search) == 0:
                    papers = r[:]
                else:
                    if in_search:
                        papers = filter_list(r, search)
                    else:
                        papers = filter_list_re(r, search)

            v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=len(papers)-1)
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
                in_search = True
            elif k == 'r':
                in_re_search = True
            elif '0' <= k <= '5':
                stars = int(k)
                papers[v.selected()].set_stars(stars)
                repo.update_paper(papers[v.selected()])


def run_ui(args, repo):
    r = repo.list()
    if len(r) == 0:
        print("Repository is empty.")
        sys.exit(0)

    if len(args) > 0:
        r = filter_list(r, args[0])

    cursor_off()
    ui_main_or_search_loop(r, repo)
    cursor_on()
    print()


