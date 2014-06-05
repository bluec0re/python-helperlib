from __future__ import absolute_import, unicode_literals

import logging
import logging.config
import re

from .terminal import TerminalController


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, *args, **kwargs):
        if fmt:
            fmt = re.sub(r'%\(level(no|name)\)s',
                         r'%(levelcolor)s%(level\1)s${NORMAL}', fmt)
        super(ColorFormatter, self).__init__(fmt, *args, **kwargs)
        self.term = TerminalController()

    def format(self, record):
        record.levelcolor = ''
        if record.levelno == logging.DEBUG:
            record.levelcolor = "${CYAN}"
        elif record.levelno == logging.INFO:
            record.levelcolor = "${GREEN}"
        elif record.levelno == logging.WARNING:
            record.levelcolor = "${YELLOW}"
        elif record.levelno == logging.ERROR:
            record.levelcolor = "${RED}"
        elif record.levelno == logging.CRITICAL:
            record.levelcolor = "${BG_RED}"

        return self.term.render(super(ColorFormatter, self).format(record))


def load_config(filename="logging.ini", *args, **kwargs):
    logging.config.fileConfig(filename, *args, **kwargs)


def default_config(level=logging.INFO, **kwargs):
    options = {
        'version': 1,
        'formatters': {
            'color': {
                '()': __name__ + '.ColorFormatter',
                'format': '[%(levelname)s] %(message)s'
                }
            },
        'filters': {},
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'color',
                'level': level,#logging.getLevelName(level),
                'stream': 'ext://sys.stdout',
                }
            },
        'loggers': {
            },
        'root': {
            'level': 'NOTSET',
            'filters': [],
            'handlers': ['console'],
            }
        }

    options.update(kwargs)

    logging.config.dictConfig(options)


if __name__ == '__main__':
    default_config(logging.DEBUG)

    log = logging.getLogger(__name__)
    log.fatal('Fatal error')
    log.critical('Critical error')
    log.error('Error')
    log.warning('Warning')
    log.info('Info')
    log.debug('Debug')
