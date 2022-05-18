import os
import sys
from collections import Counter

from .db import Db
from .config import Config
from .paper import Paper

REPO_META = ".paper"


class RepositoryV1:
    def __init__(self, config: Config, repo_meta_path):
        self.db = None
        self.config = config
        if repo_meta_path is None:
            return
        self.db = Db(repo_meta_path)
        if not self.db.check_version():
            print("Found incompatible version.")
            sys.exit(1)

    def init(self):
        """
        Creates directories, databases and updates configuration but does not change
        this isntance into a valid repository.
        :return:
        """
        # Update configuration: set default repository.
        self.config.set_default_repo(os.getcwd())
        # Create database.
        os.mkdir(os.getcwd() + "/" + REPO_META)
        self.db = Db.create(os.getcwd() + "/" + REPO_META)

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
