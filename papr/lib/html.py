import os

import markdown
from .repository import Repository


def map_header(header):
    color = {
        "Abstract": "alert-primary",
        "Notes": "alert-success",
        "Summary": "alert-danger"
    }
    return color.get(header, "btn-outline-dark")


def add_header(header):
    if header is not None:
        return '<div class="alert ' + \
               map_header(header) + ' btn-sm" role="alert" style="text-align: center; font-weight:bold">' + header + \
               '</div>'
    return ""


def ashtml(s: str, header=None):
    return "" if len(s.strip()) == 0 else \
        "<tr><td>{}{}</td></tr>".format(add_header(header), markdown.markdown(s))


def stars(n):
    return ("★"*n) + ("☆"*(5-n))


def export_html(repo: Repository, dstfile, with_notes=False, with_summary=False, n=-1):
    mydir = os.path.dirname(__file__)
    header = open(os.path.join(mydir, "../html/header.html"), "r").read()
    footer = open(os.path.join(mydir, "../html/footer.html"), "r").read()
    with open(dstfile, "w") as f:
        print(header, file=f)
        print('<table class="table">', file=f)
        cnt = 0
        for p in reversed(repo.list()):
            include = not(with_notes or with_summary)
            if with_summary:
                include = include or p.has_summary()
            if with_notes:
                include = include or p.has_notes()
            if include:
                cnt += 1
                if n != -1 and cnt > n:
                    break
                print(
                    "\n<thead class='thead-dark'><tr><th>{}</th></tr></thead>"  # title
                    "<tr><td>{}&nbsp;&nbsp;&nbsp;<a href='{}'>extern link</a></td></tr>"  # url
                    "{}"  # abstract
                    "{}"  # summary
                    "{}"  # notes
                    .format(p.title(), stars(p.stars()), p.url(),
                            ashtml(p.abstract(), "Abstract"),
                            ashtml(p.summary(), "Summary"),
                            ashtml(p.msg(), "Notes")
                            ), file=f)
        print('</table>', file=f)
        print(footer, file=f)
