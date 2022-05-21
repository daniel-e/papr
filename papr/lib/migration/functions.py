import sys
import pathlib
import yaml

from papr.lib.config import Config
from papr.lib.repository import Repository, DATA_PATH, META_FILE, path_for_paper_data
from .v1_repository import RepositoryV1, REPO_META


def assert_migration_not_needed(conf: Config):
    if _migration_needed(conf):
        print("Migration needed.")
        print("Start 'papr migrate' first.")
        sys.exit(1)


def do_migration(conf: Config):
    if not _migration_needed(conf):
        print("Migration not needed.")
        sys.exit(1)
    print("Migrating database... please wait and do not interrupt this process.")
    _do_migration(RepositoryV1(conf), conf)
    print("DONE. You can now use papr.")


def _migration_needed(conf: Config):
    r = Repository(conf)
    return not r.is_v2_repo()


def _write_file(path, filename, data):
    path.mkdir(parents=True, exist_ok=True)
    p = path.joinpath(filename)
    with open(p, "wt") as f:
        f.write(data)


def _do_migration(repo: RepositoryV1, conf: Config):
    repo_path = pathlib.Path(repo.pdf_path())
    data_path = repo_path.joinpath(DATA_PATH)  # for notes, summaries and metadata
    data_path.mkdir(parents=True, exist_ok=True)

    v2 = Repository(conf)

    for paper_v1 in repo.list():
        # path = <repo_path>/data/p00000_title_of_paper/
        path = path_for_paper_data(paper_v1, data_path)
        if paper_v1.has_summary():
            _write_file(path, "summary.md", paper_v1.summary())
            paper_v2 = v2.get_paper(paper_v1.idx())
            paper_v2.set_has_summary(True)
            v2.update_paper(paper_v2)
        if paper_v1.has_notes():
            _write_file(path, "notes.md", paper_v1.msg())
            paper_v2 = v2.get_paper(paper_v1.idx())
            paper_v2.set_has_notes(True)
            v2.update_paper(paper_v2)

    # store repository version into a file <pdf_path>/.paper/meta.yml
    meta_path = repo_path.joinpath(REPO_META).joinpath(META_FILE)
    data = {
        "repo_version": "2"
    }
    with open(meta_path, "wt") as f:
        yaml.dump(data, f)
