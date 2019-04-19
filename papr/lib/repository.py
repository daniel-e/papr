import os
import sys

from .db import Db
from .config import Config
from .paper import Paper

REPO_META = ".paper"


class Repository:
    def __init__(self, config: Config):
        self.repo_pdf_path = None
        self.repo_meta_path = None
        self.local = None
        self.db = None
        self.config = config
        self._init_paths()
        if self.is_valid():
            self.db = Db(self.repo_meta_path)
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

    def is_local_repository(self):
        return self.local

    def is_valid(self):
        """
        :return: True if this object represents a valid repository.
        """
        return self.repo_meta_path is not None and self.repo_pdf_path is not None

    def pdf_path(self):
        return self.repo_pdf_path

    def _init_paths(self):
        # First check if the current working directory is a repository.
        self.repo_pdf_path = os.getcwd()  # $PWD
        self.repo_meta_path = self.repo_pdf_path + "/" + REPO_META  # $PWD/.paper/
        self.local = True

        if not os.path.exists(self.repo_meta_path):
            # If it does not exist read the location of the repository from
            # the configuration.
            self.repo_pdf_path = self.config.get("default_repo")
            self.repo_meta_path = self.repo_pdf_path + "/" + REPO_META
            self.local = False

        if not os.path.exists(self.repo_meta_path):
            self.repo_pdf_path = None
            self.repo_meta_path = None
            self.local = None

    def list(self):
        return self.db.list()

    def next_id(self):
        return self.db.next_id()

    def add_paper(self, p: Paper):
        return self.db.add_paper(p)

    def get_paper(self, idx):
        return self.db.get(idx)

    def update_paper(self, p):
        self.db.update_paper(p)
