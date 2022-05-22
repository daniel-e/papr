import os
import pathlib
import sys
from collections import Counter

import yaml

from .db import Db
from .config import Config
from .cmd_fetch import title_as_filename

DATA_PATH = "data"      # new in v2 repository
META_FILE = "meta.yml"  # new in v2 repository
REPO_META = ".paper"    # from v1 repository

# FILES
# ------------------------------------
# <root_path>/<REPO_META>/<META_FILE> -> has the version of the repository
# <root_path>/<DATA_PATH>/p00000_...  -> directory with notes.md and summary.md


def _limit_len(s, maxlen):
    while len(s) > maxlen:
        p = s.rfind("_")
        if p >= 0:
            s = s[:p]
        else:
            s = s[:maxlen]
    return s


def path_for_paper_data(paper, data_path, maxlen=96):
    dir_name = f"{paper.idx():05d}_{title_as_filename(paper.title())}"
    return data_path.joinpath(_limit_len(dir_name, maxlen))


class Repository:
    def __init__(self, config: Config):
        self.db = None
        self.config = config
        self._valid = False

        root_path = self._determine_root()
        if not self.is_valid():
            return

        self._repo_pdf_path = root_path
        self._repo_data_path = pathlib.Path(root_path).joinpath(DATA_PATH)
        self._repo_meta_path = pathlib.Path(root_path).joinpath(REPO_META)

        self.db = Db(self._repo_meta_path, self)
        if not self.db.check_version():
            print("Found incompatible version.")
            sys.exit(1)

    def is_local_repository(self):
        root_path = os.getcwd()
        return os.path.exists(root_path + "/" + REPO_META)  # $PWD/.paper/

    def pdf_path(self):
        return self._repo_pdf_path

    def is_v2_repo(self):
        # TODO check version in that file
        return self._repo_meta_path.joinpath(META_FILE).exists()

    def _determine_root(self):
        # First check if the current working directory is a repository.
        root_path = os.getcwd()
        if os.path.exists(root_path + "/" + REPO_META):  # $PWD/.paper/
            self._valid = True
            return root_path
        # If it does not exist read the location of the repository from
        # the configuration.
        root_path = self.config.get("default_repo")
        if os.path.exists(root_path + "/" + REPO_META):  # <config_repo_root>/.paper/
            self._valid = True
            return root_path

    def is_valid(self):
        return self._valid

    def init(self):
        """
        Creates directories, databases and updates configuration but does not change
        this isntance into a valid repository.
        :return:
        """
        pdf_path = os.getcwd()
        data_path = pathlib.Path(pdf_path).joinpath(DATA_PATH)
        meta_path = pathlib.Path(pdf_path).joinpath(REPO_META)
        meta_file = meta_path.joinpath(META_FILE)

        # Update configuration: set default repository.
        self.config.set_default_repo(pdf_path)
        # Create database.
        data_path.mkdir(parents=True, exist_ok=True)
        meta_path.mkdir(parents=True, exist_ok=True)

        data = {
            "repo_version": "2"
        }
        with open(meta_file, "wt") as f:
            yaml.dump(data, f)

        self.db = Db.create(meta_path)

    def path_for_paper(self, paper):
        return path_for_paper_data(paper, self._repo_data_path)

    def summary_filename(self, paper):
        return self.path_for_paper(paper).joinpath("summary.md")

    def notes_filename(self, paper):
        return self.path_for_paper(paper).joinpath("notes.md")

    def load_paper_data(self, paper):
        summary = ""
        notes = ""
        summary_file = self.summary_filename(paper)
        if summary_file.exists():
            summary = summary_file.read_text()
        notes_file = self.notes_filename(paper)
        if notes_file.exists():
            notes = notes_file.read_text()
        data = {
            "summary": summary,
            "notes": notes
        }
        return data

    def save_summary(self, paper, summary_str):
        self.path_for_paper(paper).mkdir(parents=True, exist_ok=True)
        self.path_for_paper(paper).joinpath("summary.md").write_text(summary_str)

    def save_notes(self, paper, notes_str):
        self.path_for_paper(paper).mkdir(parents=True, exist_ok=True)
        self.path_for_paper(paper).joinpath("notes.md").write_text(notes_str)

    def list(self):
        """
        Returns a list of all papers.
        :return:
        """
        return self.db.list()

    def next_id(self):
        return self.db.next_id()

    def add_paper(self, p):
        return self.db.add_paper(p)

    def get_paper(self, idx):
        return self.db.get(idx)

    def update_paper(self, p):
        self.db.update_paper(p)

    def all_tags(self, sorted_by_usage=True):
        # Get a list of list of tags.
        l = [paper.tags() for paper in self.list_partial()]
        # Flatten the list and count the occurrences of each tag.
        c = Counter([j for i in l for j in i])
        return c.most_common()
