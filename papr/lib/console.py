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


#def cursor_right(n):
#    # http://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
#    write('\033[' + str(n) + 'C')


def cursor_bottom():
    write('\033[' + str(rows()) + 'B')
    write('\033[' + str(n) + 'B')


def cursor_top_left():
    write('\033[0;0H')


def cursor_off():
    write("\x1b[?25l")


def cursor_on():
    write("\x1b[?25h")


def cursor_goto(x, y):
    write('\033[' + str(y) + ";" + str(x) + 'H')


def write_xy(x, y, s):
    cursor_goto(x, y)
    write(s)
