import os
import sys

from .v1_db import Db
from papr.lib.config import Config

REPO_META = ".paper"


class RepositoryV1:
    def __init__(self, config: Config):
        self.db = None
        self.config = config

        # determine base_path and path for REPO_META
        self._determine_paths()

        if self.repo_meta_path is None:
            return
        self.db = Db(self.repo_meta_path)
        if not self.db.check_version():
            print("Found incompatible version.")
            sys.exit(1)

    def pdf_path(self):
        return self.repo_pdf_path

    def _determine_paths(self):
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
        """
        Returns a list of all papers.
        :return:
        """
        return self.db.list()
