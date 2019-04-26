import sys
import termcolor

from .console import cursor_on, cursor_up, cursor_off
from .edit import notes_of_paper, tags_of_paper
from .termin import read_key
from .termout import rows, empty_line, print_paper, print_header, cols
from .tools import filter_list, show_pdf
from .cmd_fetch import NEWTAG


def colwidth(s: str):
    c = cols()
    return s + (" " * (c - len(s)))


def run_ui(args, repo):
    r = repo.list()
    if len(r) == 0:
        print("Repository is empty.")
        sys.exit(0)

    if len(args) > 0:
        r = filter_list(r, args[0])

    print(termcolor.colored(" ", "white", attrs=["bold"]))
    print_header()
    m = rows() - 4 - 1             # have added -1 as otherwise the header flickers sometimes when scrolling
    n = len(r)
    window_rows = min(m, n)        # number of rows of the view
    view = n - window_rows         # index in r of the first element in the view
    selected = window_rows - 1     # row selected within the view
    initial_window_rows = window_rows
    search = ""
    in_search = False
    cursor_off()
    papers = r[:]
    while True:
        cursor_up(4)
        if in_search:
            print(termcolor.colored(colwidth("ESC: cancel + back to selection mode | ENTER: back to selection mode"), "white", "on_blue", attrs=["bold"]))
        else:
            print(termcolor.colored(colwidth("ESC/q: quit | ENTER: open | ↑: up | ↓: down | s: search | n: notes | t: tags"),
                                    "white", attrs=["bold"]))
        print_header()

        cnt = 0
        for idx, p in enumerate(papers[view:view + m]):
            print_paper(p, idx == selected)
            cnt += 1
        while cnt < initial_window_rows:
            cnt += 1
            print(empty_line())

        # search line
        sys.stdout.write(empty_line() + "\r")
        if in_search or len(search) > 0:
            sys.stdout.write("search: " + search + "▃")
            sys.stdout.flush()

        k = read_key()
        if k is None:
            cursor_up(initial_window_rows + 1)
            continue
        if not in_search:
            if k == 'i' or k == '#':
                if selected == 0:
                    view = max(view - 1, 0)
                else:
                    selected -= 1
                cursor_up(initial_window_rows + 1)
            elif k == 'k' or k == '+':
                if selected == window_rows - 1:
                    if selected + view + 1 < n:
                        view += 1
                    pass
                else:
                    selected += 1
                cursor_up(initial_window_rows + 1)
            elif k == 'n':
                notes_of_paper(repo, papers[view + selected])
                cursor_up(initial_window_rows + 1)
            elif k == 't':
                tags_of_paper(repo, papers[view + selected])
                cursor_up(initial_window_rows + 1)
            elif ord(k) == 10:
                papers[view + selected].remove_tag(NEWTAG)
                repo.update_paper(papers[view + selected])
                show_pdf(papers[view + selected], repo.pdf_path())
                cursor_up(initial_window_rows + 1)
            elif ord(k) == 27 or k == 'q':
                break
            elif k == 's':
                cursor_up(initial_window_rows + 1)
                in_search = True
            elif k >= '0' and k <= '5':
                stars = int(k)
                papers[view + selected].set_stars(stars)
                repo.update_paper(papers[view + selected])
                cursor_up(initial_window_rows + 1)
            else:
                cursor_up(initial_window_rows + 1)
        else:
            update_search = False
            if ord(k) == 27:
                in_search = False
                search = ""
                cursor_up(initial_window_rows + 1)
                update_search = True
            elif ord(k) == 10:
                in_search= False
                cursor_up(initial_window_rows + 1)
            elif ord(k) == 127:
                search = search[:-1]
                cursor_up(initial_window_rows + 1)
                update_search = True
            else:
                search += k
                cursor_up(initial_window_rows + 1)
                update_search = True
            if update_search:
                if len(search) == 0:
                    papers = r[:]
                else:
                    papers = filter_list(r, search)
                m = rows() - 4 - 1
                n = len(papers)
                window_rows = min(m, n)        # number of rows of the view
                view = n - window_rows         # index in r of the first element in the view
                selected = window_rows - 1     # row selected within the view

    cursor_on()
    print()


