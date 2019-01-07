import sys

from lib.config import Config
from lib.repository import Repository


def cmd_default(conf: Config, repo: Repository) -> None:
    if not repo.is_local_repository():
        print("You are not in a repository.")
        sys.exit(1)

    conf.set_default_repo(repo.pdf_path())


