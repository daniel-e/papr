import os
from lib.db import Db

REPO_META = ".paper"


class Repository:
    def __init__(self, config):
        self.repo_pdf_path = None
        self.repo_meta_path = None
        self.local = None
        self.db = None
        self.config = config
        self._init_paths()

    def init(self):
        # Update configuration: set default repository.
        self.config.set_default_repo(os.getcwd())
        # Create database.
        os.mkdir(os.getcwd() + "/" + REPO_META)
        self.db = Db(os.getcwd() + "/" + REPO_META)

    def is_local_repository(self):
        return self.local

    def is_valid(self):
        """
        :return: True if this object represents a valid repository.
        """
        return self.repo_meta_path and self.repo_pdf_path

    def _init_paths(self):
        # First check if the current working directory is a repository.
        repo_pdf = os.getcwd()  # $PWD
        repo_meta = repo_pdf + "/" + REPO_META  # $PWD/.paper/
        self.local = True

        if not os.path.exists(repo_meta):
            # If it does not exist read the location of the repository from
            # the configuration.
            repo_pdf = self.config.get("default_repo")
            repo_meta = repo_pdf + "/" + REPO_META
            self.repo_pdf_path = repo_pdf
            self.repo_meta_path = repo_meta
            self.local = False

        if not os.path.exists(repo_meta):
            self.repo_pdf_path = None
            self.repo_meta_path = None
            self.local = None
