from __future__ import absolute_import, unicode_literals

import sys
from .terminal import TerminalController

class _lazy(object):
    def __init__(self):
        self.term = None

    def __getattr__(self, name):
        if not self.term:
            self.term = TerminalController()
        return getattr(self.term, name)

TERM = _lazy()

def _print(text, stream=None):
    if not stream:
        stream = sys.stdout
    stream.write(TERM.render(text))
    stream.flush()


def done(stream=None):
    _print("${GREEN}DONE${NORMAL}\n", stream)


def fail(stream=None):
    _print("${RED}FAILED${NORMAL}\n", stream)


def prompt(msg=None):
    if msg:
        msg = "{} {}: ".format(_header("CYAN", "?"), msg)
    msg = TERM.render(msg)
    try:
        return raw_input(msg)
    except NameError: #py3
        return input(msg)


def _header(color, char):
    return "[${{{color}}}{char}${{NORMAL}}]".format(color=color, char=char)


def info(msg, stream=None):
    msg = "{} {}".format(_header("BLUE", "*"), msg)
    _print(msg, stream)


def success(msg, stream=None):
    msg = "{} {}\n".format(_header("GREEN", "+"), msg)
    _print(msg, stream)


def error(msg, stream=None):
    msg = "{} {}\n".format(_header("RED", "-"), msg)
    _print(msg, stream)


def exc(msg, stream=None):
    import traceback
    if not stream:
        stream = sys.stdout
    msg = "{} {}\n".format(_header("RED", "!"), msg)
    _print(msg, stream)
    traceback.print_exc(file=stream)


def warning(msg, stream=None):
    msg = "{} {}\n".format(_header("YELLOW", "~"), msg)
    _print(msg, stream)


def debug(msg, stream=None):
    msg = "{} {}\n".format(_header("MAGENTA", "|"), msg)
    _print(msg, stream)
