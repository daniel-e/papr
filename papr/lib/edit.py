import tempfile
import os
from collections import Counter
from subprocess import call

import termcolor

from .paper import Paper
from .repository import Repository


def create_tmp_file(msg):
    _, pth = tempfile.mkstemp(".tmp.md")
    f = open(pth, "wt")
    f.write(msg)
    f.close()
    return pth


# Open the string stored in _msg_ in an editor.
# Returns: content of edited file
def editor(msg, n=None):
    e = os.getenv('EDITOR', 'vim')
    pth = create_tmp_file(msg)
    cmd = [e]
    if n is not None and e == "vim":
        cmd.append("+" + str(n))
    cmd.append(pth)
    call(cmd)
    f = open(pth, "r")
    msg = f.read()
    f.close()
    return msg


def less(msg, args=[]):
    pth = create_tmp_file(msg)
    cmd = ["less", "-c"] + args + [pth]
    call(cmd)


def notes_of_paper(repo: Repository, p: Paper):
    msg = p.msg()
    msg = editor(msg, 1).strip()
    p.update_msg(msg)
    repo.update_paper(p)


def summary_of_paper(repo: Repository, p: Paper):
    summary = p.summary()
    summary = editor(summary, 1).strip()
    p.update_summary(summary)
    repo.update_paper(p)


def tags_of_paper(repo: Repository, p: Paper):
    msg = "COMMA SEPARATED LIST OF WORDS\n" + ",".join(p.tags())
    msg = editor(msg, 2)
    pos = msg.find("\n")
    if pos >= 0:
        msg = msg[pos+1:]
    msg = msg.replace("\n", ",")
    tags = [j for j in [i.strip().lower() for i in msg.split(",")] if len(j) > 0]
    p.set_tags(tags)
    repo.update_paper(p)


def abstract_of_paper(p: Paper):
    abstract = p.abstract()
    if abstract == "":
        abstract = "No abstract available."
    less(abstract)


def details_str(key, val):
    return key + ":\n" + ("=" * (len(key) + 1)) + "\n" + str(val) + "\n\n"


def details_of_paper(p: Paper):
    d = p.as_nice_dict()
    t = ""
    for key, val in {i: j for i, j in d.items() if i != "Notes"}.items():
        t += details_str(key, val)
    t += details_str("Notes", d.get("Notes", ""))
    less(t)


def bar(n, maxn, maxlen=30):
    return "█" * (maxlen * n // maxn)


def list_of_tags(repo: Repository):
    c = repo.all_tags()
    maxtaglen = max([len(tag) for tag, _ in c])
    maxn = max([n for _, n in c])
    msg = ""
    for tag, n in c:
        msg += tag + (" " * (maxtaglen - len(tag))) + " | " + "{:4}".format(n) + " " + bar(n, maxn) + "\n"
    msg += "\n\nPress q to quit."
    less(msg)


def edit_title(p: Paper, r: Repository):
    msg = editor(p.title()).strip()
    if msg != p.title():
        p.set_title(msg)
        r.update_paper(p)


def wrap_lines(s, width):
    lines = []
    while len(s) > width:
        pos = width
        while s[pos] != ' ':
            pos -= 1
        lines.append(s[:pos])
        s = s[pos+1:]
    if len(s) > 0:
        lines.append(s)
    return "\n".join(lines)


def show_summaries(repo: Repository, width):
    papers = repo.list()
    msg = ""
    width -= 1  # less has trouble to correctly show the content when not doing this
    for p in papers:
        if len(p.summary().strip()) > 0:
            t = p.title()
            d = max(0, width - len(t))
            msg += termcolor.colored(t + " " * d, "white", "on_blue", attrs=["bold"]) + "\n"
            msg += "─" * width + "\n"
            msg += wrap_lines(p.summary(), width) + "\n\n"
    msg += termcolor.colored("\nPress q to quit.", "white", "on_red", attrs=["bold"])
    less(msg, ["-r"])
