import tempfile
import os
from subprocess import call

from .paper import Paper
from .repository import Repository


def editor(msg, n=None):
    e = os.getenv('EDITOR', 'vim')
    _, pth = tempfile.mkstemp(".tmp")
    f = open(pth, "wt")
    f.write(msg)
    f.close()
    cmd = [e]
    if n is not None and e == "vim":
        cmd.append("+" + str(n))
    cmd.append(pth)
    call(cmd)
    f = open(pth, "r")
    msg = f.read()
    f.close()
    return msg


def notes_of_paper(repo: Repository, p: Paper):
    msg = p.msg()
    msg = editor(msg, 1).strip()
    p.update_msg(msg)
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
