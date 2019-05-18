import sys

from .termout import rows


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def cursor_up(n):
    # http://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
    write('\033[' + str(n) + 'A')


def cursor_down(n):
    # http://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
    write('\033[' + str(n) + 'B')


def cursor_bottom():
    write('\033[' + str(rows()) + 'B')


def cursor_top_left():
    write('\033[0;0H')


def cursor_off():
    write("\x1b[?25l")


def cursor_on():
    write("\x1b[?25h")
