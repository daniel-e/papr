import os
import termios
import sys
from select import select


def read_key():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    c = []
    try:
        select([fd], [], [])
        c = [i for i in os.read(fd, 50)]
    except IOError:
        pass
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    if len(c) == 1:
        return chr(c[0])
    else:
        if c == [27, 91, 65]:
            return '#'
        elif c == [27, 91, 66]:
            return '+'
