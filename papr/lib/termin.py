import os
import termios
import sys
from select import select

from .termout import cols, rows


def read_key():
    n_cols = cols()
    n_rows = rows()

    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    c = []
    try:
        while True:
            r1, r2, r3 = select([fd], [], [], 0.05)
            if not r1 and not r2 and not r3: # timeout -> check if size of terminal has changed
                if n_cols != cols() or n_rows != rows():
                    c = [0, 1, 2]
                    break
            else:
                c = [i for i in os.read(fd, 50)]
                break
    except IOError:
        pass
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    if len(c) == 1:
        return chr(c[0])
    else:
        if c == [0, 1, 2]:  # redraw screen
            return '~'
        elif c == [27, 91, 65]:
            return '#'
        elif c == [27, 91, 66]:
            return '+'
        elif c == [27, 91, 49, 59, 50, 65]: # shift + up
            return '['
        elif c == [27, 91, 49, 59, 50, 66]: # shift + down
            return ']'
        elif c == [27, 91, 54, 126]: # page down
            return '§'
        elif c == [27, 91, 53, 126]: # page up
            return '$'
        #print(c)
        #while True:
        #    pass

