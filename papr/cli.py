#!/usr/bin/env python3
import os
import re
import shutil
import sqlite3
import sys
import json
import termios
import urllib
from subprocess import Popen, DEVNULL
import urllib.request

from bs4 import BeautifulSoup
import termcolor

REPO_NAME = ".paper"
SQLITE_FILE = "paper.db"
CONFIG_FILE = "paper.cfg"
VIEWER = "/usr/bin/evince"


def help(exitcode=0):
    print("Usage: " + sys.argv[0] + " [COMMAND] [OPTION]...\n")
    print("COMMANDS")
    hr()
    print("init       Create a new repository in the current directory.")
    print("list       List all tracked papers in the current repository.")
    print("pop        Read the paper with the largest ID.")
    print("search <regex>")
    print("           List all papers for which the regex matches the title.")
    print("fetch  <file> <title>")
    print("           Add a paper to the repository. The file is copied to the repository.")
    print("           Filename will be <idx>_<normalized_title>.pdf")
    print("       <url> [title]")
    print("           Download a paper and add it to the repository. If the URL points to")
    print("           a pdf title is required. If the URL points to a web page which")
    print("           contains the title and a link to the pdf in a recognized format")
    print("           title is not required and the pdf will be downloaded.")
    print("add    <file> [idx]")
    print("           Add a file which is located in the repository directory but which")
    print("           is not tracked yet. The filename does not change and will be used")
    print("           as the title without the extension.")
    print("select [regex]")
    print()
    sys.exit(exitcode)


def cursor_off():
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()


def cursor_on():
    sys.stdout.write("\x1b[?25h")
    sys.stdout.flush()


def assert_in_repo():
    if not os.path.exists(REPO_NAME):
        print("You are not in a paper repository.", file=sys.stderr)
        sys.exit(1)


def create_directory():
    if os.path.exists(REPO_NAME):
        print("You are already in a paper repository.", file=sys.stderr)
        sys.exit(1)
    try:
        os.mkdir(REPO_NAME)
    except OSError as err:
        print("Error", err)
        sys.exit(1)


def sqlite_file():
    return REPO_NAME + "/" + SQLITE_FILE


def db_create():
    conn = sqlite3.connect(sqlite_file())
    # TODO: handle error if connect fails
    c = conn.cursor()
    c.execute("CREATE TABLE papers (idx integer primary key, json text)")
    conn.commit()
    conn.close()
    # TODO: handle db errors


class Paper:
    def __init__(self, idx, filename, title):
        self.idx = idx
        self.filename = filename
        self.title = title

    @staticmethod
    def from_json(idx, jsonstr):
        p = Paper(idx, filename=None, title=None)
        p.idx = idx
        data = json.loads(jsonstr)
        p.filename = data["filename"]
        p.title = data["title"]
        return p

    def as_json(self):
        d = {"filename": self.filename, "title": self.title}
        return json.dumps(d)


def db_list():
    conn = sqlite3.connect(sqlite_file())
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


def create_config():
    d = {"version": "0.0.1"}
    cfgfile = REPO_NAME + "/" + CONFIG_FILE
    f = open(cfgfile, "w")
    f.write(json.dumps(d))
    f.close()


def cmd_init(args):
    create_directory()
    create_config()
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
        f = f[:n - 4] + " ..."
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
            p = int(100.0 * (s - n) / s)
            N = 40
            l = int(p * N / 100)
            done = "█" * l
            todo = "." * (N - l)
            sys.stdout.write("\r|{}{}| {:3d}% ".format(done, todo, p))
            sys.stdout.flush()
        print()
    else:
        chars = "▏▎▍▌▋▊▉█"
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


def show_pdf(p):
    #print("File :", p.filename)
    #print("Title:", p.title)
    Popen([VIEWER, p.filename], stderr=DEVNULL, stdout=DEVNULL)


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
    r = re.compile(q.lower())
    if r.search(p.title.lower()):
        return True
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


def cmd_pop():
    assert_in_repo()
    r = db_list()
    if len(r) == 0:
        print("empty")
        return
    show_pdf(r[-1])


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


def cursor_up(n):
    # http://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
    print('\033[' + str(n) + 'A')


def cmd_select(args):
    r = db_list()
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
            sys.stdout.write("search: " + search)
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
                show_pdf(papers[view + selected])
                cursor_up(initial_window_rows+ 1)
            elif ord(k) == 27 or k == 'q':
                break
            elif k == 's':
                cursor_up(initial_window_rows + 1)
                in_search = True
                cursor_on()
            else:
                cursor_up(initial_window_rows + 1)
        else:
            update_search = False
            if ord(k) == 27:
                in_search = False
                cursor_off()
                search = ""
                cursor_up(initial_window_rows + 1)
                update_search = True
            elif ord(k) == 10:
                in_search= False
                cursor_off()
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


def parse_command():
    if len(sys.argv) < 2:
        help(1)
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
    elif c == "pop":
        cmd_pop()
    elif c == "add":
        cmd_add(sys.argv[2:])
    elif c == "select":
        cmd_select(sys.argv[2:])
    else:
        help(1)


def main():
    parse_command()


if __name__ == "__main__":
    main()
