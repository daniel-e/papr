import sys


def cmd_init(repo) -> None:
    # Check that the current directory isn't already a repository.
    if repo.is_local_repository():
        print("You are already in a repository.", file=sys.stderr)
        sys.exit(1)
    # Create repository.
    repo.init()
    print("Repository created.")


