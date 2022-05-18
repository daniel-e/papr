import os

import yaml

from .config import Config
from .paper import Paper
from .repository_v1 import RepositoryV1, REPO_META
from .repository_v2 import RepositoryV2, DATA_PATH, META_FILE


class Repository:
    def __init__(self, config: Config):
        self._repo_pdf_path = None
        self._repo_meta_path = None
        self._local = None
        self._proxy = None
        self._config = config
        self._determine_paths()

        # TODO: eventuell muss init_path oder init hier implementiert werden, denn wir müssen hier
        # berücksichtigen, ob wir uns in einem repo befinden oder außerhalb (und deshalb das default_repo verwenden)

        if self._is_v1():
            self._proxy = RepositoryV1(config, self._repo_meta_path)
        elif self._is_v2():
            self._proxy = RepositoryV2(config, self._repo_pdf_path)

    def _is_v1(self):
        return not os.path.exists(self._repo_pdf_path + "/" + REPO_META + "/"  + META_FILE)

    def _is_v2(self):
        p = self._repo_pdf_path + "/" + REPO_META + "/" + META_FILE
        if os.path.exists(p):
            with open(p, "rt") as f:
                y = yaml.safe_load(f)
                return int(y.get("repo_version", 0)) == 2
        return False

    def is_local_repository(self):
        return self._local

    def is_valid(self):
        """
        :return: True if this object represents a valid repository.
        """
        return self._repo_meta_path is not None and self._repo_pdf_path is not None

    def pdf_path(self):
        return self._repo_pdf_path

    def _determine_paths(self):
        # First check if the current working directory is a repository.
        self._repo_pdf_path = os.getcwd()  # $PWD
        self._repo_meta_path = self._repo_pdf_path + "/" + REPO_META  # $PWD/.paper/
        self._local = True

        if not os.path.exists(self._repo_meta_path):
            # If it does not exist read the location of the repository from
            # the configuration.
            self._repo_pdf_path = self._config.get("default_repo")
            self._repo_meta_path = self._repo_pdf_path + "/" + REPO_META
            self._local = False

        if not os.path.exists(self._repo_meta_path):
            self._repo_pdf_path = None
            self._repo_meta_path = None
            self._local = None

    # Called by the user via "papr init".
    def init(self):
        """
        Creates directories, databases and updates configuration but does not change
        this isntance into a valid repository.
        :return:
        """
        self._proxy.init()

    def list(self):
        """
        Returns a list of all papers.
        :return:
        """
        return self._proxy.list()

    def next_id(self):
        return self._proxy.next_id()

    def add_paper(self, p: Paper):
        return self._proxy.add_paper(p)

    def get_paper(self, idx):
        return self._proxy.get_paper(idx)

    def update_paper(self, p):
        self._proxy.update_paper(p)

    def all_tags(self, sorted_by_usage=True):
        return self._proxy.all_tags(sorted_by_usage=sorted_by_usage)
