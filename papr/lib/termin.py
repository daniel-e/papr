import termios
import sys


def read_key():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    c = None
    try:
        c = sys.stdin.read(1)
    except IOError:
        pass
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return c


