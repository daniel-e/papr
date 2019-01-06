#!/usr/bin/env python3

# Settings -> Project: papr -> Project Structure
#   use only papr as "Sources"

import sys
import math
import os
import re
import shutil
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
from lib.term import rows, empty_line, print_papers, print_header, print_paper
from lib.help import help
from lib.cmd_add import cmd_add


VIEWER = "/usr/bin/evince"


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


def cmd_search(args, repo: Repository):
    if len(args) == 0:
        print("You need to specify a query.")
        sys.exit(1)
    r = repo.list()
    if len(r) == 0:
        print("empty")
        return
    r = filter_list(r, args[0])
    if len(r) == 0:
        print("Not found.")
    else:
        print_papers(r)


def cmd_last(args, repo: Repository):
    p = -1
    if len(args) > 0:
        p = -int(args[0])
    r = repo.list()
    if len(r) == 0:
        print("empty")
        return
    show_pdf(r[p], repo.pdf_path())


def cmd_read(args, repo):
    if len(args) == 0:
        print("You need to specify a paper id.")
        sys.exit(1)
    p = repo.get_paper(int(args[0]))
    if not p:
        print("Not found.")
        sys.exit(1)
    show_pdf(p, repo.pdf_path())


def cmd_list(repo):
    r = repo.list()
    if len(r) == 0:
        print("empty")
    else:
        print_header()
        print_papers(r)


def show_pdf(p, repo_path):
    Popen([VIEWER, repo_path + "/" + p.filename], stderr=DEVNULL, stdout=DEVNULL)


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


def normalize_title(s):
    return re.sub(r'\s+', " ", s.replace("\n", " "))


def title_as_filename(s):
    return re.sub(r'[^a-z0-9]', "_", re.sub(r'\s+', "_", s.lower()))


def prepare_data(title: str, repo: Repository):
    title = normalize_title(title)
    idx = repo.next_id()
    filename = "{:05d}_{}.pdf".format(idx, title_as_filename(title))
    return title, idx, filename


def add_local_file(f: str, args, repo: Repository):
    if len(args) == 0:
        print("For local files you need to specify the title of the paper.")
        sys.exit(1)

    title, idx, filename = prepare_data(args[0], repo)
    if not os.path.exists(filename):
        shutil.copy(f, filename)
    p = Paper(idx=idx, filename=filename, title=title)
    repo.add_paper(p)
    print("Added paper.")
    print("Title:", title)
    print("Filename:", filename)


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


def cmd_fetch(args, repo: Repository):
    if len(args) == 0:
        print("You need to specify a filename or URL.")
        sys.exit(1)

    fname = args[0]
    if os.path.exists(fname):
        add_local_file(fname, args[1:], repo)
    else:
        req = urllib.request.Request(fname)
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

        title, idx, filename = prepare_data(title, repo)

        k = open(filename, "w")
        k.buffer.write(data)
        k.close()

        p = Paper(idx=idx, filename=filename, title=title)
        repo.add_paper(p)
        print("Added paper.")
        print("Title:", title)
        print("Filename:", filename)


def cmd_select(args, repo):
    r = repo.list()
    if len(r) == 0:
        print("Repository is empty.")
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
                show_pdf(papers[view + selected], repo.pdf_path())
                cursor_up(initial_window_rows+ 1)
            elif ord(k) == 27 or k == 'q':
                break
            elif k == 's':
                cursor_up(initial_window_rows + 1)
                in_search = True
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


def cmd_default(conf: Config, repo: Repository) -> None:
    if not repo.is_local_repository():
        print("You are not in a repository.")
        sys.exit(1)

    conf.set_default_repo(repo.pdf_path())


def cmd_init(repo: Repository) -> None:
    # Check that the current directory isn't already a repository.
    if repo.is_local_repository():
        print("You are already in a repository.", file=sys.stderr)
        sys.exit(1)
    # Create repository.
    repo.init()
    print("Repository created.")


def parse_command(conf: Config, repo: Repository) -> None:
    if len(sys.argv) > 1:
        c = sys.argv[1]
        if c == "init":
            cmd_init(repo)
            return
        elif c == "default":
            cmd_default(conf, repo)
            return

    # For all other commands we need a valid repository.
    if not repo.is_valid():
        print("No repository.")
        sys.exit(1)

    # no arguments given -> show select menu
    if len(sys.argv) < 2:
        cmd_select(sys.argv[2:], repo)
        sys.exit(0)

    c = sys.argv[1]
    if c == "list":
        cmd_list(repo)
    elif c == "fetch":
        cmd_fetch(sys.argv[2:], repo)
    elif c == "read":
        cmd_read(sys.argv[2:], repo)
    elif c == "search":
        cmd_search(sys.argv[2:], repo)
    elif c == "last":
        cmd_last(sys.argv[2:], repo)
    elif c == "add":
        cmd_add(sys.argv[2:], repo)
    elif c == "help" or c == "--help" or c == "-h":
        help(0)
    else:
        help(1)


def main() -> None:
    # Reads the configuration from "~/.papr/". Creates a default config if
    # it doesn't exist yet.
    conf = Config()
    # If we are in a repository create an instance of this repository. If we
    # are not in a repository create an instance of the default repository. If
    # there is no default repository, Repository.is_valid() will return False.
    r = Repository(conf)
    parse_command(conf, r)


if __name__ == "__main__":
    main()
