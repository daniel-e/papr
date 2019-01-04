#!/usr/bin/env python3

# Settings -> Project: papr -> Project Structure
#   use only papr as "Sources"

import sys
import math
import os
import re
import shutil
import sqlite3
import termios
import urllib
from subprocess import Popen, DEVNULL
import urllib.request
from bs4 import BeautifulSoup
import termcolor

from lib.config import Config
from lib.paper import Paper
from lib.console import cursor_off, cursor_on, cursor_up
from lib.repository import Repository

SQLITE_FILE = "paper.db"
CONFIG_FILE = "paper.cfg"
VIEWER = "/usr/bin/evince"
HOME_DIR = ".papr"
HOME_FILE = "papr.cfg"




def command():
    s = sys.argv[0]
    return s if s.rfind("/") < 0 else s[s.rfind("/")+1:]


def help(exitcode=0):
    print("Usage: " + command() + " [search regex] | <command> [<args>]\n")
    print("Commands")
    hr()
    print("  help       This help message.")
    print("\nRepository commands")
    print("  init       Create a new repository in the current directory and sets it to")
    print("             the default repository.\n")
    print("  default    Set the current repository as default repository.")
    print("\nList papers")
    print("  list       List all tracked papers in the current repository.\n")
    print("  search <regex>")
    print("             List all papers for which the regex matches the title.")
    print("\nReading papers")
    print("  read <id>  Read paper with given ID.\n")
    print("  last [<n>] Read the paper with the n-th largest ID. default: n = 1")
    print("\nAdding papers")
    print("  fetch  <file> <title>")
    print("             Add a paper to the repository.  The file is copied to the")
    print("             repository. Filename will be <idx>_<normalized_title>.pdf")
    print("")
    print("         <url> [title]")
    print("             Download a paper and add it to the repository. If the URL points")
    print("             to a pdf title is required. If the URL points to a web page which")
    print("             contains the title and a link to the pdf in a recognized format")
    print("             title is not required and the pdf will be downloaded.")
    print("")
    print("  add    <file> [idx]")
    print("             Add a file which is located in the repository directory but which")
    print("             is not tracked yet. The filename does not change and will be used")
    print("             as the title without the extension.")
    print()
    sys.exit(exitcode)


def assert_in_repo():
    if not os.path.exists(REPO_META):
        print("You are not in a paper repository.", file=sys.stderr)
        sys.exit(1)


def create_directory():
    if os.path.exists(REPO_META):
        print("You are already in a paper repository.", file=sys.stderr)
        sys.exit(1)
    try:
        os.mkdir(REPO_META)
    except OSError as err:
        print("Error", err)
        sys.exit(1)


def repo_path():
    c = Config(REPO_META, CONFIG_FILE, HOME_DIR)
    r = ""
    if os.path.exists(REPO_META):
        r = "."
    else:
        d = c.read_config()
        n = d["default_repo"]
        if n == "null":
            print("No repository.", file=sys.stderr)
            sys.exit(1)
        r = n
    return r


def repo_idx_path():
    c = Config(REPO_META, CONFIG_FILE, HOME_DIR)
    r = ""
    if os.path.exists(REPO_META):
        r = REPO_META
    else:
        d = c.read_config()
        n = d["default_repo"]
        if n == "null":
            print("No repository.", file=sys.stderr)
            sys.exit(1)
        r = n + "/" + REPO_META
    return r


def sqlite_file():
    return repo_idx_path() + "/" + SQLITE_FILE


def db_create():
    conn = sqlite3.connect(sqlite_file())
    # TODO: handle error if connect fails
    c = conn.cursor()
    c.execute("CREATE TABLE papers (idx integer primary key, json text)")
    conn.commit()
    conn.close()
    # TODO: handle db errors


class DB:
    def __init__(self, repo_paths):
        self.repo_paths = repo_paths

    def _sqlite_file(self):
        return self.repo_paths.repo_meta + "/" + SQLITE_FILE

    def db_list(self):
        conn = sqlite3.connect(self._sqlite_file())
        # TODO: handle error if connect fails
        c = conn.cursor()
        r = [Paper.from_json(j[0], j[1]) for j in sorted([i for i in c.execute("SELECT idx, json FROM papers")])]
        conn.close()
        # TODO: handle db errors
        return r


def db_add_paper(p):
    conn = sqlite3.connect(sqlite_file())
    # TODO: handle error if connect fails
    c = conn.cursor()
    data = (p.idx, p.as_json())
    c.execute("INSERT INTO papers (idx, json) VALUES (?, ?)", data)
    conn.commit()
    conn.close()
    # TODO: handle db errors


def db_next_id():
    conn = sqlite3.connect(sqlite_file())
    # TODO: handle error if connect fails
    c = conn.cursor()
    r = [i[0] for i in c.execute("SELECT idx FROM papers")]
    conn.close()
    # TODO: handle db errors
    if len(r) == 0:
        return 1
    return max(r) + 1


def db_get(idx):
    conn = sqlite3.connect(sqlite_file())
    # TODO: handle error if connect fails
    c = conn.cursor()
    r = c.execute("SELECT json FROM papers WHERE idx=" + str(idx))
    r = r.fetchone()
    conn.close()
    # TODO: handle db errors
    if not r:
        return None
    return Paper.from_json(idx, r[0])


def cmd_init(args):
    c = Config(REPO_META, CONFIG_FILE, HOME_DIR)
    create_directory()
    c.create_config()
    c.update_default_repo()
    db_create()
    print("Repository created.")


def rows():
    _, rows = os.get_terminal_size(0)
    return rows


def hr():
    cols, _ = os.get_terminal_size(0)
    print("─" * cols)


def print_header():
    cols, _ = os.get_terminal_size(0)
    print("Id    Title " + " " * (cols - 12))
    hr()
    return cols


def empty_line():
    cols, _ = os.get_terminal_size(0)
    return " " * cols


def print_paper(paper, selected = False):
    cols, _ = os.get_terminal_size(0)
    # 5 columns for id
    # 1 columns for space
    # cols - (5 + 1) columns for filename
    n = cols - (5 + 1)
    f = paper.title
    if len(f) > n:
        f = f[:n - 3] + "..."
    s = "{:5d} {}".format(paper.idx, f)
    if len(s) < cols:
        s = s + (" " * (cols - len(s)))
    if selected:
        print(termcolor.colored(s, 'white', 'on_red', attrs=["bold"]))
    else:
        print(termcolor.colored(s, 'white'))


def print_papers(papers):
    for paper in papers:
        print_paper(paper)


def cmd_list(args):
    assert_in_repo()
    r = db_list()
    if len(r) == 0:
        print("empty")
    else:
        print_header()
        print_papers(r)


def normalize_title(s):
    return re.sub(r'\s+', " ", s.replace("\n", " "))


def title_as_filename(s):
    return re.sub(r'[^a-z0-9]', "_", re.sub(r'\s+', "_", s.lower()))


def prepare_data(title):
    title = normalize_title(title)
    idx = db_next_id()
    filename = "{:05d}_{}.pdf".format(idx, title_as_filename(title))
    return title, idx, filename


def add_local_file(f, args):
    if len(args) == 0:
        print("For local files you need to specify the title of the paper.")
        sys.exit(1)
    title, idx, filename = prepare_data(args[0])
    if not os.path.exists(filename):
        shutil.copy(f, filename)
    p = Paper(idx=idx, filename=filename, title=title)
    db_add_paper(p)
    print("Added paper.")
    print_papers([p])


def is_text_or_html(s):
    return s is not None and (s.lower().find("text") >= 0 or s.lower().find("html") >= 0)


def bar(p):
    chars = "▏▎▍▌▋▊▉█"
    N = 40
    l = p * N / 100.0
    todo = "." * (N - int(l))
    done = "█" * int(l)

    f = l - math.floor(l)
    if f > 0:
        todo = "." * (N - int(l) - 1)
        done = done + chars[int(f * len(chars))]

    r = str(int(255 - 255 * p / 100.0))
    g = str(int(255 * p / 100.0))
    b = "0"
    #sys.stdout.write("\r|\x1b[1;33m{}\x1b[0m{}| {:3d}% ".format(done, todo, int(p)))
    sys.stdout.write("\r|\x1b[38;2;{};{};{}m{}\x1b[0m{}| {:3d}% ".format(r, g, b, done, todo, int(p)))
    sys.stdout.flush()


def download(rsp):
    n = rsp.getheader("content-length")
    data = bytes()
    if n is not None:
        n = int(n)
        s = n
        while n > 0:
            t = rsp.read(min(1024, n))
            data += t
            n -= min(1024, n)
            bar(100.0 * (s - n) / s)
        print()
    else:
        chars = "|/-|\\"
        n = 0
        while True:
            t = rsp.read(10240)
            if len(t) == 0:
                break
            data += t
            sys.stdout.write("\rloading " + chars[n % len(chars)])
            sys.stdout.flush()
            n += 1
        print("\r          ")
    return data


def parse_page(data):
    h = BeautifulSoup(data, "html.parser")
    r = h.find_all("meta")
    title = [i.get("content") for i in r if i.get("name") == "citation_title"]
    pdfurl = [i.get("content") for i in r if i.get("name") == "citation_pdf_url"]
    if len(title) > 0 and len(pdfurl) > 0:
        return title[0], pdfurl[0]
    return None, None


def cmd_fetch(args):
    assert_in_repo()
    if len(args) == 0:
        print("You need to specify a filename or URL.")
        sys.exit(1)
    f = args[0]
    if os.path.exists(f):
        add_local_file(f, args[1:])
    else:
        req = urllib.request.Request(f)
        rsp = urllib.request.urlopen(req)
        typ = rsp.getheader("content-type")
        if not is_text_or_html(typ) and len(args) < 2:  # for PDF files we need a title
            print("The response is not html. You need to specify a title.")
            sys.exit(1)
        data = download(rsp)
        title = ""
        if is_text_or_html(typ):
            t, pdfurl = parse_page(data)
            if t is None:
                print("Error")
                sys.exit(1)
            title = t
            req = urllib.request.Request(pdfurl)
            rsp = urllib.request.urlopen(req)
            data = download(rsp)
        else:
            title = args[1]

        title, idx, filename = prepare_data(title)

        k = open(filename, "w")
        k.buffer.write(data)
        k.close()

        p = Paper(idx=idx, filename=filename, title=title)
        db_add_paper(p)
        print("Added paper.")
        print_papers([p])


def show_pdf(p, repo_paths):
    Popen([VIEWER, repo_paths.repo_pdf + "/" + p.filename], stderr=DEVNULL, stdout=DEVNULL)


def cmd_read(args):
    assert_in_repo()
    if len(args) == 0:
        print("You need to specify a paper id.")
        sys.exit(1)
    p = db_get(int(args[0]))
    if not p:
        print("Not found.")
        sys.exit(1)
    show_pdf(p)


def exists_in(p, q):
    try:
        r = re.compile(q.lower())
        if r.search(p.title.lower()):
            return True
        return False
    except Exception:
        return False


def filter_list(l, query):
    return [i for i in l if exists_in(i, query)]


def cmd_search(args):
    assert_in_repo()
    if len(args) == 0:
        print("You need to specify a query.")
        sys.exit(1)
    r = db_list()
    if len(r) == 0:
        print("empty")
        return
    r = filter_list(r, args[0])
    if len(r) == 0:
        print("Not found.")
    else:
        print_papers(r)


def cmd_last(args):
    p = -1
    if len(args) > 0:
        p = -int(args[0])
    assert_in_repo()
    r = db_list()
    if len(r) == 0:
        print("empty")
        return
    show_pdf(r[p])


def cmd_add(args):
    assert_in_repo()
    if len(args) == 0:
        print("You need to specify a filename.")
        sys.exit(1)
    filename = args[0]
    idx = db_next_id()
    if len(args) > 1:
        idx = int(args[1])
    title = filename
    if title.rfind(".") >= 0:
        title = title[:title.rfind(".")]
    p = Paper(idx=idx, filename=filename, title=title)
    db_add_paper(p)
    print("Added paper.")
    print_papers([p])


def read_key():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    c = None
    try:
        c = sys.stdin.read(1)
    except IOError:
        pass
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return c

def cmd_select(args, repo_paths):
    db = DB(repo_paths)
    r = db.db_list()
    if len(r) == 0:
        print("empty")
        sys.exit(0)
    if len(args) > 0:
        r = filter_list(r, args[0])
    print(termcolor.colored("ESC or q: quit | ENTER: open paper | i: up | k: down | s: search", "white", attrs=["bold"]))
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
            print(termcolor.colored("ESC: cancel + back to selection mode | ENTER: back to selection mode", "white", attrs=["bold"]))
        else:
            print(termcolor.colored("ESC or q: quit | ENTER: open paper | i: up | k: down | s: search    ", "white", attrs=["bold"]))
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
        if not in_search:
            if k == 'i':
                if selected == 0:
                    view = max(view - 1, 0)
                else:
                    selected -= 1
                cursor_up(initial_window_rows + 1)
            elif k == 'k':
                if selected == window_rows - 1:
                    if selected + view + 1 < n:
                        view += 1
                    pass
                else:
                    selected += 1
                cursor_up(initial_window_rows + 1)
            elif ord(k) == 10:
                show_pdf(papers[view + selected], repo_paths)
                cursor_up(initial_window_rows+ 1)
            elif ord(k) == 27 or k == 'q':
                break
            elif k == 's':
                cursor_up(initial_window_rows + 1)
                in_search = True
                #cursor_on()
            else:
                cursor_up(initial_window_rows + 1)
        else:
            update_search = False
            if ord(k) == 27:
                in_search = False
                #cursor_off()
                search = ""
                cursor_up(initial_window_rows + 1)
                update_search = True
            elif ord(k) == 10:
                in_search= False
                #cursor_off()
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


def cmd_default():
    c = Config(REPO_META, CONFIG_FILE, HOME_DIR)
    c.update_default_repo()


def parse_command():
    # no arguments given -> show select menu
    if len(sys.argv) < 2:
        cmd_select(sys.argv[2:], paths())
        sys.exit(0)

    c = sys.argv[1]
    if c == "init":
        cmd_init(sys.argv[2:])
    elif c == "list":
        cmd_list(sys.argv[2:])
    elif c == "fetch":
        cmd_fetch(sys.argv[2:])
    elif c == "read":
        cmd_read(sys.argv[2:])
    elif c == "search":
        cmd_search(sys.argv[2:])
    elif c == "last":
        cmd_last(sys.argv[2:])
    elif c == "add":
        cmd_add(sys.argv[2:])
    elif c == "help" or c == "--help" or c == "-h":
        help(0)
    elif c == "default":
        cmd_default()
    else:
        cmd_select(sys.argv[2:])


def main():
    conf = Config()
    repo = Repository(conf)
    if not repo.is_valid():
        print("No repository.")
        sys.exit(1)

    parse_command()


if __name__ == "__main__":
    main()
