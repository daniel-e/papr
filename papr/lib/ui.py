import sys
import termcolor

from .console import cursor_on, cursor_up, cursor_off
from .edit import notes_of_paper, tags_of_paper, abstract_of_paper, details_of_paper, list_of_tags
from .termin import read_key
from .termout import rows, empty_line, print_paper, cols
from .tools import filter_list, show_pdf
from .cmd_fetch import NEWTAG


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


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


# The last element is selected.
class ScrollView():
    def __init__(self, n_elements, rows, selected):
        self.n_elemens = n_elements
        self.rows = rows
        self._selected = selected    # selected is in [0..n_elements-1]
        self.first_element_in_view = max(0, n_elements - rows)

    def up(self):
        if self.first_element_in_view == self._selected:
            self.first_element_in_view = max(self.first_element_in_view - 1, 0)
        self._selected = max(0, self._selected - 1)

    def down(self):
        if self._selected == self.first_element_in_view + self.rows - 1:
            self.first_element_in_view = min(self.first_element_in_view + 1, self.n_elemens - self.rows)
        self._selected = min(self._selected + 1, self.n_elemens - 1)

    def selected(self):
        return self._selected

    def first(self):
        return self.first_element_in_view

    def end(self):
        return self.first_element_in_view + self.rows


def run_ui(args, repo):
    r = repo.list()
    if len(r) == 0:
        print("Repository is empty.")
        sys.exit(0)

    if len(args) > 0:
        r = filter_list(r, args[0])

    cursor_off()
    write(build_title())

    n_window_rows = rows() - 1

    n_papers = len(r)
    n_view_rows = n_window_rows - 3 - 1
    # -3 = 3 rows for header
    # -1 = 1 row for search line
    v = ScrollView(n_elements=n_papers, rows=n_view_rows, selected=n_papers-1)

    search = ""
    in_search = False
    papers = r[:]

    while True:
        if in_search:
            write(build_search_header())
        else:
            write(build_default_header())
        write(build_header())

        cnt = 0 + 3
        for idx, p in enumerate(papers[v.first():v.end()]):
            print_paper(p, idx + v.first() == v.selected())
            cnt += 1
        # clear remaining lines
        while cnt < n_window_rows - 1:
            cnt += 1
            write(empty_line())

        # search line
        sys.stdout.write(empty_line() + "\r")
        if in_search or len(search) > 0:
            sys.stdout.write("search: " + search + "▃")
            sys.stdout.flush()

        cnt += 1

        k = read_key()
        if k is None:
            cursor_up(cnt)
            continue
        if not in_search:
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
            elif '0' <= k <= '5':
                stars = int(k)
                papers[v.selected()].set_stars(stars)
                repo.update_paper(papers[v.selected()])
        else:
            update_search = False
            if ord(k) == 27:
                in_search = False
                search = ""
                update_search = True
            elif ord(k) == 10:
                in_search = False
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
                    papers = filter_list(r, search)

            v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=len(papers)-1)
        cursor_up(cnt)
    cursor_on()
    print()


