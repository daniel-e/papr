import sys
from .termout import _hr


def command():
    s = sys.argv[0]
    return s if s.rfind("/") < 0 else s[s.rfind("/")+1:]


def help(exitcode=0):
    print("Usage: " + command() + " [search regex] | <command> [<args>]")
    print("")
    print("Start papr without any arguments to start the text UI.")
    print("")
    print("Commands")
    _hr()
    print("  help       This help message.")
    print("\nRepository commands")
    print("  init       Create a new repository in the current directory and sets it to")
    print("             the default repository.\n")
    print("  default    Set the current repository as default repository.")
    print("")
    print("List papers")
    print("  list       List all tracked papers in the current repository.\n")
    print("  search <regex>")
    print("             List all papers for which the regex matches the title.")
    print("")
    print("Reading papers")
    print("  read <id>  Read paper with given ID.\n")
    print("  last [<n>] Read the paper with the n-th largest ID. default: n = 1")
    print("")
    print("Adding papers")
    print("  fetch  <file> <title>")
    print("             Add a paper to the repository.  The file is copied to the")
    print("             repository. Filename will be <idx>_<normalized_title>.pdf")
    print("")
    print("         <url> [title]")
    print("             Download a paper and add it to the repository. If the URL points")
    print("             to a pdf title is required. If the URL points to a web page which")
    print("             contains the title and a link to the pdf in a recognized format")
    print("             title is not required and the pdf will be downloaded.")
    print("")
    print("         --urls <filename>")
    print("             Load papers for the URLs stored in a file. (one URL per line)")
    print("")
    print("  add    <file> [idx]")
    print("             Add a file which is located in the repository directory but which")
    print("             is not tracked yet. The filename does not change and will be used")
    print("             as the title without the extension.")
    print()
    sys.exit(exitcode)
