from __future__ import absolute_import, unicode_literals

import logging
import sys
import os
from traceback import format_exception


__all__ = [
     'add_exceptionhook', 'rm_exceptionhook', 'uncaught_hook', 'install_hook'
]

_hooks = []


def uncaught_hook(exc_class, exc_inst, trb):
    """

    Keyword arguments:
    exc_class --
    exc_inst --
    trb --

    """
    if isinstance(exc_inst, KeyboardInterrupt):
        sys.exit(0)
    elif isinstance(exc_inst, SystemExit):
        sys.exit(exc_inst.value)

    logging.fatal("Uncaught exception: %s\n%s", exc_inst,
                  ''.join(format_exception(exc_class, exc_inst, trb)))

    if os.environ.get('JIT_DEBUG'):
        import pdb
        pdb.post_mortem(trb)


def hook(*args, **kwargs):
    """

    Keyword arguments:
    *args --
    **kwargs --

    """
    for h in _hooks:
        h(*args, **kwargs)


def add_exceptionhook(h):
    """
    add exception hook to the hook listener

    Keyword arguments:
    h -- the hook
    """
    _hooks.insert(0, h)


def rm_exceptionhook(h):
    """
    rm exception hook from the hook listener

    Keyword arguments:
    h -- the hook
    """
    i = _hooks.find(h)
    if i > -1:
        del _hooks[i]


def install_hook():
    """
    install the uncaught exception hook listener
    """
    _hooks.append(uncaught_hook)
    sys.excepthook = hook
