import tempfile
import os
from subprocess import call

from lib.paper import Paper
from lib.repository import Repository


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
    if len(msg) == 0:
        msg = "Notes\n" + "============================================================\n"
    msg = editor(msg, 2).strip()
    lines = msg.split()
    if len(lines) > 1:
        if lines[0] == "Notes" and lines[1] == "============================================================":
            del lines[0]
            del lines[0]
    msg = "\n".join(lines)
    p.update_msg(msg)
    repo.update_paper(p)
