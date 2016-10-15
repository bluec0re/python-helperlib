from __future__ import absolute_import, unicode_literals

import logging
import logging.config
import re
import threading
import os

from .terminal import TerminalController


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, *args, **kwargs):
        if fmt:
            fmt = re.sub(r'%\(level(no|name)\)\d*s',
                         r'%(levelcolor)s\g<0>${NORMAL}', fmt)
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
    """
    Load logger config from file
    
    Keyword arguments:
    filename -- configuration filename (Default: "logging.ini")
    *args -- options passed to fileConfig
    **kwargs -- options passed to fileConfigg
    
    """
    logging.config.fileConfig(filename, *args, **kwargs)


def default_config(level=logging.INFO, auto_init=True, **kwargs):
    """
    Returns the default config dictionary and inits the logging system if requested
    
    Keyword arguments:
    level -- loglevel of the console handler (Default: logging.INFO)
    auto_init -- initialize the logging system with the provided config (Default: True)
    **kwargs -- additional options for the logging system
    
    """
    options = {
        'version': 1,
        'disable_existing_loggers': False,
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
                'stream': 'ext://sys.stderr',
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
    
    if auto_init:
        logging.config.dictConfig(options)
    return options


def scope_logger(cls):
    """
    Class decorator for adding a class local logger

    Example:
    >>> @scope_logger
    >>> class Test:
    >>>     def __init__(self):
    >>>         self.log.info("class instantiated")
    >>> t = Test()
    
    """
    cls.log = logging.getLogger('{0}.{1}'.format(cls.__module__, cls.__name__))
    return cls


class LogPipe(threading.Thread):

    def __init__(self, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        super(LogPipe, self).__init__(name='LogPipe')
        self.daemon = False
        self.level = logging._checkLevel(level)
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self._finished = threading.Event()
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        self._finished.clear()
        for line in iter(self.pipeReader.readline, ''):
            logging.log(self.level, line.strip('\n'))

        self.pipeReader.close()
        self._finished.set()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)
        self._finished.wait()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

if __name__ == '__main__':
    default_config(logging.DEBUG)

    log = logging.getLogger(__name__)
    log.fatal('Fatal error')
    log.critical('Critical error')
    log.error('Error')
    log.warning('Warning')
    log.info('Info')
    log.debug('Debug')


    import subprocess
    with LogPipe('INFO') as logPipe:
        subprocess.check_call(['ls'], stdout=logPipe)
