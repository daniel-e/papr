import os
import sys
from pathlib import Path

import termcolor

from .latest_version import latest_version
from .config import Config
from .console import cursor_on, cursor_off, cursor_top_left, cursor_up, cursor_down, write_xy
from .edit import edit_notes_of_paper, tags_of_paper, abstract_of_paper, details_of_paper, list_of_tags, edit_title, \
    edit_summary_of_paper, show_summaries
from .html import export_repository_html
from .termin import read_key
from .termout import rows, empty_line, print_paper, cols, write
from .tools import filter_list, show_pdf, filter_list_re, highlight_query, show_in_browser
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


def build_title(conf):
    current_v = conf.papr_version()
    s = "papr " + current_v
    v = conf.latest_version()
    if len(v) > 0 and v != current_v:
        s += " (new version available)"
    return termcolor.colored(
        expand_to_colwidth(s),
        "white", "on_blue", attrs=["bold"])


def extent(s, width):
    return s + (" " * (width - len(s)))


# TODO copy&paste
def write_box_xy(x, y, content, select_lineno=None, wmax=None, arrow_down=False, arrow_up=False):
    if not wmax:
        wmax = max([len(c) for c in content])
    write_xy(x, y, colored("┌" + ("─" * wmax) + "┐", "white", "on_blue"))
    y += 1
    for idx, s in enumerate(content):
        write_xy(x, y, colored("│", "white", "on_blue"))
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
        y += 1
    write_xy(x, y, colored("└" + ("─" * wmax) + "┘", "white", "on_blue"))


# content: List of strings
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


def redraw(state, papers, v, conf):
    cursor_top_left()
    write(build_title(conf))

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
            " e             : Edit title.",
            " 0..5          : Set voting.",
            " y             : Show all stored information about a paper.",
            " l             : Show statistics about tags.",
            " f             : Filter (e.g. by tags).",
            " F             : Clear filter.",
            " c             : Hide/show paper.",
            " .             : Show hidden/visible papers.",
            " space         : Open a context menu.",
            " m             : List all papers with a summary.",
            " b             : Open web browser for details."
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

        self.show_hidden = False
        self.show_menu = False


def center_box(content):
    posy = max(0, rows() // 2 - len(content) // 2)
    posx = max(0, cols() // 2 - max([len(i) for i in content]) // 2)
    return posx, posy


def show_new_features(conf: Config):
    message = [
        "CHANGES FROM 0.0.18 TO 0.0.20",
        "-----------------------------",
        "• Navigation",
        "  • Shift+Up/Down - jump 5 entries up/down",
        "  • Page Up/Down  - jump one page up/down"
        "• Fetch",
        "  • You can now specify more than just one URL for fetch command.",
        "  • You can now specify tags for fetch command.",
        "• Storage for notes and summary more open and accessible. You can now",
        "  read and edit your notes and summaries without papr.",
        "• Export to HTML.",
        "• Minor improvements to UI."
#        "",
#        "CHANGES FROM 0.0.17 TO 0.0.18",
#        "-----------------------------",
#        "• You can now change the title of a paper with the key 'e'.",
#        "• Never miss a new version! If a new version is available, it will be",
#        "  shown at the top of the screen.",
#        "  For this the setup.py from the GitHub repository is retrieved and",
#        "  checked.",
#        "• When you upgrade papr to the latest version this message with changes",
#        "  is shown on the first start.",
#        "• You can hide papers with the key 'c'. Use the same key to make hidden",
#        "  papers visible again. You can change between the list of hidden and",
#        "  visible papers with the key '.'",
#        "• Press 'space' to get a context menu.",
#        "• You can already create notes for a paper. Now, you can also create a",
#        "  summary. Just select 'edit summary' from the context menu or use the",
#        "  shortcut 'U'. List all papers with a summary with the shortcut 'm'."
    ]
    posx, posy = center_box(message)
    write_box_xy(posx, posy, message)


def select_item(menu):
    posx, posy = center_box(menu)
    selection = 0
    while True:
        write_box_xy(posx, posy, menu, select_lineno=selection)
        k = read_key()
        if ord(k) == 27 or k == 'q':
            return None
        elif ord(k) == 10:  # Enter
            return selection
        elif k == 'i' or k == '#':
            selection = max(0, selection - 1)
        elif k == 'k' or k == '+':
            selection = min(len(menu) - 1, selection + 1)


def ui_main_or_search_loop(papers_in, repo: Repository, conf: Config):
    n_papers = len(papers_in)
    n_view_rows = rows() - 3 - 1 - 1
    # -3 = 3 rows for header
    # -1 = 1 row for search line
    # -1 = 1 "papr" header line
    v = ScrollView(n_elements=n_papers, rows=n_view_rows, selected=n_papers-1)

    s = State()
    papers = papers_in[:]

    while True:
        if s.show_hidden:
            filtered_papers = [p for p in papers if p.hidden()]
            if len(filtered_papers) != len(papers):
                papers = filtered_papers
                pos = min(v.selected(), len(papers) - 1)
                v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=pos)
        else:
            # Filter hidden papers
            filtered_papers = [p for p in papers if not p.hidden()]
            if len(filtered_papers) != len(papers):
                papers = filtered_papers
                pos = min(v.selected(), len(papers) - 1)
                v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=pos)



        cursor_off()
        redraw(s, papers, v, conf)

        # If a new version is started for the first time show the new features.
        if not conf.new_features_already_shown():
            show_new_features(conf)
            read_key()
            continue

        # Menu
        k = None
        if s.show_menu:
            values = [
                [" Edit notes                  ", "n"],
                [" Edit title                  ", "e"],
                [" Edit tags                   ", "t"],
                [" Edit summary                ", "U"],
                [" Show abstract               ", "a"],
                [" Show details                ", "y"]
            ]
            menu = [i[0] for i in values]
            k = select_item(menu)
            if k is not None:
                k = values[k][1]
            s.show_menu = False
        else:
            k = read_key()

        if k is None or k == '~':
            continue

        if s.in_search or s.in_re_search:
            for p in papers:
                p.set_highlights([])
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

            papers = f(papers_in, s.search)
            # highlight search
            if s.in_search:
                for p in papers:
                    positions = highlight_query(p, s.search)
                    p.set_highlights(positions)

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
                elif k == '[':
                    s.tag_scrollview.up(5)
                elif k == ']':
                    s.tag_scrollview.down(5)
                elif k == '§':
                    s.tag_scrollview.pagedown()
                elif k == '$':
                    s.tag_scrollview.pageup()
                elif ord(k) == 10:
                    s.selected_tag = s.tags[s.tag_scrollview.selected()][0]
                    papers = [p for p in papers_in if s.selected_tag in p.tags()]
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
            elif k == '[':
                v.up(5)
            elif k == ']':
                v.down(5)
            elif k == '§':
                v.pagedown()
            elif k == '$':
                v.pageup()
            elif k == 'n':
                edit_notes_of_paper(repo, papers[v.selected()])
            elif k == 'U':
                edit_summary_of_paper(repo, papers[v.selected()])
            elif k == 't':
                tags_of_paper(repo, papers[v.selected()])
            elif ord(k) == 10:
                p = v.selected()
                papers[p].remove_tag(NEWTAG)
                repo.update_paper(papers[p])
                show_pdf(papers[p], repo.pdf_path(), conf.get_viewer())
            elif ord(k) == 27 or k == 'q':
                break
            elif k == 's':
                s.in_search = True
                # copy&paste from above
                for p in papers:
                    positions = highlight_query(p, s.search)
                    p.set_highlights(positions)
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
                papers = papers_in[:]
                v = ScrollView(n_elements=len(papers), rows=n_view_rows, selected=len(papers) - 1)
                # TODO: consider search
            elif k == 'h':
                s.in_help = True
            elif k == 'e':
                edit_title(papers[v.selected()], repo)
            elif k == 'c':
                p = papers[v.selected()]
                p.hide(not p.hidden())
                repo.update_paper(p)
            elif k == '.':
                s.show_hidden = not s.show_hidden
                papers = papers_in[:]
            elif k == ' ':
                s.show_menu = True
            elif k == 'm':
                show_summaries(repo, cols())
            elif k == 'x':
                file_dialog(repo, conf)
            elif k == 'b':
                show_in_browser(repo, papers[v.selected()], conf.get_browser(), conf.get_browser_params())


# TODO duplicate code
def show_dialog(x, y, width, header="", content=None):
    write_xy(x, y, colored("┌" + ("─" * width) + "┐", "white", "on_blue"))
    y += 1
    for idx, s in enumerate(header):
        write_xy(x, y, colored("│", "white", "on_blue"))
        write(colored(extent(s, width), "white", "on_blue"))
        write(colored("│", "white", "on_blue"))
        y += 1
    if content is not None:
        write_xy(x, y, colored("│", "white", "on_blue"))
        write(colored(extent(content, width), "white", "on_red", True))
        write(colored("│", "white", "on_blue"))
        y += 1
    write_xy(x, y, colored("└" + ("─" * width) + "┘", "white", "on_blue"))


# TODO make it reusable
def file_dialog(repo: Repository, conf: Config):
    width = min(cols() - 2, 40)
    y = rows() // 2 - 2
    x = cols() // 2 - width // 2
    s = conf.get_export_path(os.path.join(str(Path.home()), "papers.html"))
    while True:
        val = s + "▃"
        if len(s) >= width:
            val = val[-width:]
        show_dialog(x, y, width, header=["Filename for export:"], content=val)
        key = read_key()
        if key is None:
            continue
        if ord(key) == 27:
            break
        elif ord(key) == 10:
            conf.set_export_path(s)
            export_repository_html(repo, s)
            show_dialog(x, y, width, header=["Repository exported to:", s[:width]])
            read_key()
            break
        elif ord(key) == 127:
            s = s[:-1]
        elif key.isprintable():
            s += key


def run_ui(args, repo: Repository, conf: Config):
    papers = repo.list()
    if len(papers) == 0:
        print("Repository is empty.")
        sys.exit(0)

    if len(args) > 0:
        papers = filter_list(papers, args[0])

    # Retrieve latest version of papr from GitHub.
    latest_version(conf.set_latest_version)

    ui_main_or_search_loop(papers, repo, conf)
    cursor_on()
    print()


