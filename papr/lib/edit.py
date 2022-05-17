import tempfile
import os
import unittest
from collections import Counter
from subprocess import call

import termcolor

from .paper import Paper
from .repository import Repository

MARKDOWN_HELP = """┌───────────────────────────────────────────────────┐
│ Markdown Help (will be removed automatically)     │
├───────────────────────────────────────────────────┤
│ ### This is a title.                              │
│                                                   │
│ - This is a                                       │
│ - list                                            │
│   This line belongs to the previous point.        │
│                                                   │
│ This is **bold** and *italic* and `inline code`.  │
│                                                   │
│ A horizontal line:                                │
│ - - -                                             │
│                                                   │
│ This is a [link](https://).                       │
│                                                   │
│ You can create tables:                            │
│                                                   │
│ Column 1 | Column 2                               │
│ -------- | ---------                              │
│ Foo      | Bar                                    │
└───────────────────────────────────────────────────┘"""


def create_tmp_file(content="", ext="tmp.md"):
    _, pth = tempfile.mkstemp("." + ext)
    f = open(pth, "wt")
    f.write(content)
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


def insert_markdown_help(msg):
    return msg + "\n" + MARKDOWN_HELP


def remove_markdown_help(msg):
    for i in ["\n", ""]:
        s = i + MARKDOWN_HELP
        pos = msg.find(s)
        if pos >= 0:
            msg = msg[:pos] + msg[pos + len(s):]
    return msg


def notes_of_paper(repo: Repository, p: Paper):
    msg = p.msg()
    msg = insert_markdown_help(msg)
    msg = editor(msg, 1).strip()
    msg = remove_markdown_help(msg)
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


class TestEdit(unittest.TestCase):
    def test_insert_and_remove_markdown(self):
        msg = ""
        msg = insert_markdown_help(msg)
        self.assertEqual(msg, "\n" + MARKDOWN_HELP)
        msg = remove_markdown_help(msg)
        self.assertEqual(msg, "")

        msg = "A"
        msg = insert_markdown_help(msg)
        self.assertEqual(msg, "A\n" + MARKDOWN_HELP)
        msg = remove_markdown_help(msg)
        self.assertEqual(msg, "A")

        msg = "A\n"
        msg = insert_markdown_help(msg)
        self.assertEqual(msg, "A\n\n" + MARKDOWN_HELP)
        msg = remove_markdown_help(msg)
        self.assertEqual(msg, "A\n")


if __name__ == "__main__":
    unittest.main()