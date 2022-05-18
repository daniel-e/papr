import os
import pathlib
import sys
from collections import Counter

from .db_v2 import Db
from .config import Config
from .paper import Paper
from .repository_v1 import REPO_META

DATA_PATH = "data"
META_FILE = "meta.yml"

# FILES
# ------------------------------------
# <pdf_path>/<REPO_META>/<META_FILE> -> has the version of the repository
# <pdf_path>/<DATA_PATH>/p00000_...  -> directory with notes.md and summary.md


class RepositoryV2:
    def __init__(self, config: Config, pdf_path):
        self.db = None
        self.config = config

        if pdf_path is None:
            return

        self._repo_pdf_path = pdf_path
        self._repo_data_path = pathlib.Path(pdf_path).joinpath(DATA_PATH)
        self._repo_meta_path = pathlib.Path(pdf_path).joinpath(REPO_META)

        self.db = Db(self._repo_meta_path)
        if not self.db.check_version():
            print("Found incompatible version.")
            sys.exit(1)

    def init(self):
        """
        Creates directories, databases and updates configuration but does not change
        this isntance into a valid repository.
        :return:
        """
        pdf_path = os.getcwd()
        data_path = pathlib.Path(pdf_path).joinpath(DATA_PATH)
        meta_path = pathlib.Path(pdf_path).joinpath(REPO_META)

        # Update configuration: set default repository.
        self.config.set_default_repo(pdf_path)
        # Create database.
        data_path.mkdir(parents=True, exist_ok=True)
        meta_path.mkdir(parents=True, exist_ok=True)
        self.db = Db.create(meta_path)

    def list(self):
        """
        Returns a list of all papers.
        :return:
        """
        return self.db.list()

    def next_id(self):
        return self.db.next_id()

    def add_paper(self, p: Paper):
        return self.db.add_paper(p)

    def get_paper(self, idx):
        return self.db.get(idx)

    def update_paper(self, p):
        self.db.update_paper(p)

    def all_tags(self, sorted_by_usage=True):
        # Get a list of list of tags.
        l = [paper.tags() for paper in self.list()]
        # Flatten the list and count the occurrences of each tag.
        c = Counter([j for i in l for j in i])
        return c.most_common()
