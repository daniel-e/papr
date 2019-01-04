import os

REPO_META = ".paper"


class Repository:
    def __init__(self, config):
        self.config = config
        self._init_paths()

    def is_valid(self):
        """
        :return: True if this object represents a valid repository.
        """
        return self.repo_meta_path and self.repo_pdf_path

    def _init_paths(self):
        # First check if the current working directory is a repository.
        repo_pdf = os.getcwd()  # $PWD
        repo_meta = repo_pdf + "/" + REPO_META  # $PWD/.paper/

        if not os.path.exists(repo_meta):
            # If it does not exist read the location of the repository from
            # the configuration.
            repo_pdf = self.config.get["default_repo"]
            repo_meta = repo_pdf + "/" + REPO_META
            self.repo_pdf_path = repo_pdf
            self.repo_meta_path = repo_meta

        if not os.path.exists(repo_meta):
            self.repo_pdf_path = None
            self.repo_meta_path = None
