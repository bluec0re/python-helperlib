from __future__ import absolute_import, unicode_literals

import logging
import sys
from traceback import format_exception

_hooks = []

def uncaught_hook(exc_class, exc_inst, trb):
    if isinstance(exc_inst, KeyboardInterrupt):
        sys.exit(0)
    elif isinstance(exc_inst, SystemExit):
        sys.exit(exc_inst.value)

    logging.fatal("Uncaught exception: %s\n%s", exc_inst,
                  ''.join(format_exception(exc_class, exc_inst, trb)))


def hook(*args, **kwargs):
    for h in _hooks:
        h(*args, **kwargs)


def add_exceptionhook(h):
    _hooks.insert(0, h)


def rm_exceptionhook(h):
    i = _hooks.find(h)
    if i > -1:
        del _hooks[i]


def install_hook():
    _hooks.append(uncaught_hook)
    sys.excepthook = hook
