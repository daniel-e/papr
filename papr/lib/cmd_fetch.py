import math
import sys
import urllib
import urllib.request
import os
import shutil
import re
import argparse

import yaml
from bs4 import BeautifulSoup

from .html import export_repository_html
from .paper import Paper
from .edit import editor
from .abstract import parse_abstract


NEWTAG="unread"


def title_as_filename(s):
    # lower case
    s = re.sub(r'\s+', "_", s.lower())
    # remove everything except a-z0-9
    s = re.sub(r'[^a-z0-9]', "_", s)
    # remove double _
    s = re.sub(r'_+', '_', s)
    # remove trailing _
    s = re.sub(r'_+$', '', s)
    return s


def normalize_title(s):
    return re.sub(r'\s+', " ", s.replace("\n", " "))


def prepare_data(title: str, repo):
    title = normalize_title(title)
    idx = repo.next_id()
    filename = "{:05d}_{}.pdf".format(idx, title_as_filename(title))
    abspath = repo.pdf_path() + "/" + filename
    return title, idx, filename, abspath


def add_local_file(f: str, title, repo, tags):
    tmp_title = ""
    if len(title) == 0:
        tmp_title = determine_title_via_vim()
    else:
        tmp_title = title

    title, idx, filename, abspath = prepare_data(tmp_title, repo)
    if not os.path.exists(abspath):
        shutil.copy(f, abspath)
    p = Paper(idx=idx, filename=filename, title=title, tags=[NEWTAG]+tags)
    repo.add_paper(p)
    print("Added paper.")
    print("Title   :", title)
    print("Filename:", filename)


def is_text_or_html(s):
    return s is not None and (s.lower().find("text") >= 0 or s.lower().find("html") >= 0)


def white():
    return "\x1b[97;1m"


def reset():
    return "\x1b[0m"


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


def download(rsp, no_progress_bar=False):
    n = rsp.getheader("content-length")
    data = bytes()
    if n is not None:
        n = int(n)
        s = n
        while n > 0:
            t = rsp.read(min(1024, n))
            data += t
            n -= min(1024, n)
            if not no_progress_bar:
                bar(100.0 * (s - n) / s)
        if not no_progress_bar:
            print()
    else:
        chars = "|/-|\\"
        n = 0
        while True:
            t = rsp.read(10240)
            if len(t) == 0:
                break
            data += t
            if not no_progress_bar:
                sys.stdout.write("\rloading " + chars[n % len(chars)])
                sys.stdout.flush()
            n += 1
        if not no_progress_bar:
            print("\r          ")
    return data


def parse_page(data):
    h = BeautifulSoup(data, "html.parser")
    r = h.find_all("meta")
    title = [i.get("content") for i in r if i.get("name") == "citation_title"]
    pdfurl = [i.get("content") for i in r if i.get("name") == "citation_pdf_url"]
    abstract = parse_abstract(data)
    if len(title) > 0 and len(pdfurl) > 0:
        return title[0], pdfurl[0], abstract
    return None, None, None


def determine_title_via_vim():
    msg = "# Please enter the title of the paper.\n\n"
    msg = editor(msg, 2)
    s = ""
    for line in msg.split("\n"):
        c = re.compile(r"\s*#.*")
        m = c.match(line)
        if m is None:
            s = (s + " " + line.strip()).strip()
    if len(s) == 0:
        s = "(emtpy)"
    return s


def do_fetch_download(repo, url, title, tags):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    rsp = urllib.request.urlopen(req)
    typ = rsp.getheader("content-type")
    if not is_text_or_html(typ) and title == "":  # for PDF files we need a title
        title = determine_title_via_vim()
    data = download(rsp, is_text_or_html(typ))
    abstract = ""
    if is_text_or_html(typ):
        t, pdfurl, abstract = parse_page(data)
        if t is None:
            print("Error")
            sys.exit(1)
        title = t
        req = urllib.request.Request(pdfurl)
        rsp = urllib.request.urlopen(req)
        data = download(rsp)

    title, idx, filename, abspath = prepare_data(title, repo)

    k = open(abspath, "w")
    k.buffer.write(data)
    k.close()

    p = Paper(idx=idx, filename=filename, title=title, tags=[NEWTAG]+tags)
    p.set_url(url)
    p.set_abstract(abstract)
    repo.add_paper(p)
    print("{}{}{} {}".format(white(), "   Title:", reset(), title))
    print("{}{}{} {}".format(white(), "Filename:", reset(), filename))
    print("{}{}{} {}".format(white(), "Abstract:", reset(), abstract))
    print("{}{}{}".format(white(), "Added paper.", reset()))
    print()


def do_fetch(location, title, repo, tags):
    if title is None:
        title = ""
    if os.path.exists(location):
        add_local_file(location, title, repo, tags=tags)
    else:
        do_fetch_download(repo, url=location, title=title, tags=tags)


def cmd_fetch(args, repo):
    parser = argparse.ArgumentParser(description="Fetch a paper.")
    parser.add_argument("--urls", nargs=1, required=False, metavar="filename", help="Load papers from URLs stored in a file. (one URL per line)")
    parser.add_argument("-t", nargs=1, required=False, type=str, help="Title of paper.")
    parser.add_argument("--tags", nargs=1, required=False, type=str, help="Comma separated list of tags.")
    parser.add_argument("location", nargs='*', type=str)
    #parser.print_help()
    args = parser.parse_args(args)

    title = ""
    if args.t is not None:
        title = args.t[0]

    tags = []
    if args.tags is not None:
        tags = [i.strip() for i in args.tags[0].split(",")]

    if args.urls is not None:
        with open(args.urls[0], "r") as f:
            for line in f:
                s = line.strip()
                if len(s) > 0:
                    print("fetching", s, "...", file=sys.stderr)
                    do_fetch(s, title, repo, tags)
    else:
        for location in args.location:
            try:
                do_fetch(location, title, repo, tags)
            except:
                pass


def cmd_export_html(args, repo):
    parser = argparse.ArgumentParser(description="Export the database into an HTML file.")
    parser.add_argument("--with-note", action='store_true', help="Export papers only if they contain notes.")
    parser.add_argument("--with-summary", action='store_true', help="Export papers only if they contain a summary.")
    parser.add_argument("-n", type=int, default=-1, help="Export the n most recent papers.")
    parser.add_argument("filename", nargs=1, type=str)
    args = parser.parse_args(args)
    export_repository_html(repo, args.filename[0], with_notes=args.with_note, with_summary=args.with_summary, n=args.n)


def cmd_export_yml(args, repo):
    parser = argparse.ArgumentParser(description="Export the database into a YML file.")
    parser.add_argument("filename", nargs=1, type=str, description="YML file.")
    args = parser.parse_args(args)

    # TODO export summary (paper.summary()) and notes (paper.msg()) as well

    path = args.filename[0]
    all_meta = []
    for paper in repo.list():
        meta = {
            "title": paper.title(),
            "stars": paper.stars(),
            "idx": paper.idx(),
            "pdf": paper.filename(),
            "tags": ",".join(paper.tags()),
            "abstract": paper.abstract(),
            "url": paper.url(),
        }
        all_meta.append(meta)
    with open(path, "wt") as f:
        yaml.dump(all_meta, f)
