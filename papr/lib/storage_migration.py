import pathlib
import yaml

from .repository import Repository, Paper, Config, DATA_PATH, REPO_META, META_FILE
from .cmd_fetch import title_as_filename


def limit_len(s, maxlen):
    while len(s) > maxlen:
        p = s.rfind("_")
        if p >= 0:
            s = s[:p]
        else:
            s = s[:maxlen]
    return s


def path_for_paper(paper: Paper, data_path, maxlen):
    dir_name = f"{paper.idx():05d}_{title_as_filename(paper.title())}"
    return data_path.joinpath(limit_len(dir_name, maxlen))


def write_file(path, filename, data):
    path.mkdir(parents=True, exist_ok=True)
    p = path.joinpath(filename)
    with open(p, "wt") as f:
        f.write(data)


def do_migration(conf: Config, repo: Repository):
    maxlen = 96
    repo_path = pathlib.Path(repo.pdf_path())
    data_path = repo_path.joinpath(DATA_PATH)  # for notes, summaries and metadata
    data_path.mkdir(parents=True, exist_ok=True)

    for paper in repo.list():
        # path = <repo_path>/data/p00000_title_of_paper/
        path = path_for_paper(paper, data_path, maxlen)
        if paper.has_summary():
            write_file(path, "summary.md", paper.summary())
        if paper.has_notes():
            write_file(path, "notes.md", paper.msg())

    # store repository version into a file <pdf_path>/.paper/meta.yml
    meta_path = repo_path.joinpath(REPO_META).joinpath(META_FILE)
    data = {
        "repo_version": "2"
    }
    with open(meta_path, "wt") as f:
        yaml.dump(data, f)
