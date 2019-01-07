import math
import sys
import urllib
import urllib.request
import os
import shutil
import re
from bs4 import BeautifulSoup

from lib.paper import Paper
from lib.repository import Repository


def title_as_filename(s):
    return re.sub(r'[^a-z0-9]', "_", re.sub(r'\s+', "_", s.lower()))


def normalize_title(s):
    return re.sub(r'\s+', " ", s.replace("\n", " "))


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


