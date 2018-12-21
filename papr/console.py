import sys


def cursor_up(n):
    # http://tldp.org/HOWTO/Bash-Prompt-HOWTO/x361.html
    print('\033[' + str(n) + 'A')


def cursor_off():
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()


def cursor_on():
    sys.stdout.write("\x1b[?25h")
    sys.stdout.flush()
