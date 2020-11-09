import os

import markdown
from .repository import Repository


def map_header(header):
    color = {
        "Abstract": "btn-outline-primary",
        "Notes": "btn-outline-success",
        "Summary": "btn-outline-danger"
    }
    return color.get(header, "btn-outline-dark")


def add_header(header):
    if header is not None:
        return '<button type="button" class="btn ' + \
               map_header(header) + ' btn-sm">' + header + \
               '</button>'
    return ""


def ashtml(s: str, header=None):
    return "" if len(s.strip()) == 0 else \
        "<tr><td>{}{}</td></tr>".format(add_header(header), markdown.markdown(s))


def stars(n):
    return ("★"*n)+("☆"*(5-n))


def export_html(repo: Repository, dstfile):
    mydir = os.path.dirname(__file__)
    header = open(os.path.join(mydir, "../html/header.html"), "r").read()
    footer = open(os.path.join(mydir, "../html/footer.html"), "r").read()
    with open(dstfile, "w") as f:
        print(header, file=f)
        print('<table class="table">', file=f)
        for p in reversed(repo.list()):
            print(
                "<thead class='thead-dark'><tr><th>{}</th></tr></thead>"  # title
                "<tr><td>{}&nbsp;&nbsp;&nbsp;<a href='{}'>{}</a></td></tr>"  # url
                "{}"  # abstract
                "{}"  # summary
                "{}"  # notes
                .format(p.title(), stars(p.stars()), p.url(), p.url(),
                        ashtml(p.abstract(), "Abstract"),
                        ashtml(p.summary(), "Summary"),
                        ashtml(p.msg(), "Notes")), file=f)
        print('</table>', file=f)
        print(footer, file=f)
