import os

import markdown
from .paper import Paper


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
        "<tr><td>{}{}</td></tr>".format(add_header(header), markdown.markdown(s, extensions=['tables']))


def stars(n):
    return ("★"*n) + ("☆"*(5-n))


def export_paper_html(repo, p: Paper, f, with_pdf_link=False):
    pdf_link = ""
    if with_pdf_link:
        pdf_link = \
            "<a href='file://{}' class='btn btn-outline-secondary btn-sm role='button'>local pdf</a>" \
            .format(os.path.join(repo.pdf_path(), p.filename()))
    extern_link = "extern link"
    if p.url().find("arxiv.org") != -1:
        extern_link = "on arXiv"
    print(
        "<thead class='thead-dark'><tr><th>{}</th></tr></thead>"  # title
        "<tr>"
        "  <td>{}&nbsp;&nbsp;&nbsp;<a href='{}' class='btn btn-outline-secondary btn-sm role='button'>{}</a> {}</td>"
        "</tr>"  # url
        "{}"  # abstract
        "{}"  # summary
        "{}"  # notes
            .format(p.title(), stars(p.stars()), p.url(), extern_link, pdf_link,
                    ashtml(p.abstract(), "Abstract"),
                    ashtml(p.summary(), "Summary"),
                    ashtml(p.msg(), "Notes")
                    ), file=f)


def export_repository_html(repo, dstfile, with_notes=False, with_summary=False, n=-1):
    papers = reversed(repo.list())
    export_papers_html(repo, papers, dstfile, with_notes, with_summary, n)


def export_papers_html(repo, papers, dstfile, with_notes=False, with_summary=False, n=-1, with_pdf_link=False):
    mydir = os.path.dirname(__file__)
    header = open(os.path.join(mydir, "../html/header.html"), "r").read()
    footer = open(os.path.join(mydir, "../html/footer.html"), "r").read()
    with open(dstfile, "w") as f:
        print(header, file=f)
        print('<table class="table">', file=f)
        cnt = 0
        for p in papers:
            include = not(with_notes or with_summary)
            if with_summary:
                include = include or p.has_summary()
            if with_notes:
                include = include or p.has_notes()
            if include:
                cnt += 1
                if n != -1 and cnt > n:
                    break
                export_paper_html(repo, p, f, with_pdf_link=with_pdf_link)
        print('</table>', file=f)
        print(footer, file=f)
