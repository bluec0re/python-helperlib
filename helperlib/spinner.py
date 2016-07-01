#  vim: set ts=8 sw=4 tw=0 fileencoding=utf-8 filetype=python expandtab:
from __future__ import absolute_import, unicode_literals

import sys
import time
from .exception import add_exceptionhook
from .internal import _print

def _trace(s):
    _print(s, sys.stderr)

def _debug(s):
    _print(s, sys.stderr)

def _billboard(msg, step):
    return [msg[i:i+step].ljust(step, ' ') for i in range(len(msg))]


if sys.stderr.isatty():
    import threading
    _spinner = None
    _message = ''
    _status = ''
    _lock = threading.Lock()

    class _Spinner(threading.Thread):
        def __init__(self):
            import random
            threading.Thread.__init__(self)
            self.running = True
            self.i = 0
            self.numlines = 0
            self.spinner = random.choice([
                ['/.......','./......','../.....','.../....','..../...','...../..','....../.',
                 '.......\\','......\\.','.....\\..','....\\...','...\\....','..\\.....','.\\......'],
#                _billboard('   8=================D~~~   D:  ', 5),
                _billboard('   trollololol lololol lololol     trollolololoooool      ', 5),
                ['|', '/', '-', '\\'],
                ['q', 'p', 'b', 'd'],
                ['.', 'o', 'O', '0', '*', ' ', ' ', ' '],
                ['▁', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃'],
                ['┤', '┘', '┴', '└', '├', '┌', '┬', '┐'],
                ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
                ['◢', '◢', '◣', '◣', '◤', '◤', '◥', '◥'],
                ['◐', '◓', '◑', '◒'],
                ['▖', '▘', '▝', '▗'],
                ['.', 'o', 'O', '°', ' ', ' ', '°', 'O', 'o', '.', ' ', ' '],
                ['<', '<', '∧', '∧', '>', '>', 'v', 'v']
            ])

        def format(self, marker, status):
            s = '\x1b[J ' + marker + ' ' + _message
            if status and _message:
                s += ': '
            lines = status.split('\n')
            lines += [''] * (self.numlines - len(lines) - 1)
            if len(lines) > 1:
                if lines[0] == '':
                    lines = lines[1:]
                pref = '\n       '
                s += pref
                s += pref.join(lines)
                self.numlines = len(lines) + 1
            else:
                s += status
            return s

        def update(self, only_spin = False):
            _lock.acquire()
            marker = "[${BOLD}${BLUE}%s${NORMAL}]" % (self.spinner[self.i],)
            if only_spin:
                _trace('\x1b[s ' + marker + '\x1b[u')
            else:
                s = self.format(marker, _status)
                if self.numlines <= 1:
                    s += '\x1b[G'
                else:
                    s += '\x1b[%dF' % (self.numlines - 1)
                _trace(s)
            _lock.release()

        def finish(self, marker, status):
            if not status:
                _trace(marker + '\x1b[%dE\n' % self.numlines)
            elif '\n' not in status:
                s = '\x1b[K' + marker + ' ' + _message + ': ' + status
                if self.numlines > 1:
                    s += '\x1b[%dE' % (self.numlines - 1)
                s += '\n'
                _trace(s)
            else:
                _trace(self.format(marker, status) + '\n')
            _trace('\x1b[?25h')

        def run(self):
            global _marker
            while True:
                if self.running:
                    self.update(True)
                else:
                    break
                self.i = (self.i + 1) % len(self.spinner)
                time.sleep(0.1)

    def _stop_spinner(marker = '[${BOLD}${BLUE}*${NORMAL}]', status = ''):
        global _spinner, _status

        if _spinner is None:
            return

        _spinner.running = False
        _spinner.join()
        _spinner.finish(marker, status)
        _spinner = None

    def _hook(*args):
        global _spinner
        _stop_spinner('')
        _trace('${BOLD}${YELLOW}[!]${NORMAL} BOOOM\n')

    add_exceptionhook(_hook) # reset, show cursor

    def _start_spinner():
        global _spinner
        _stop_spinner()
        _spinner = _Spinner()
        _spinner.update()
        _spinner.daemon = True
        _spinner.start()

    def trace(s):
        _stop_spinner()
        _trace(s)

    def debug(s):
        _stop_spinner()
        _debug(s)

    def waitfor(s):
        global _message, _status
        if _spinner is not None:
            raise Exception('waitfor has already been called')
        _status = ''
        _message = s
        _start_spinner()

    def status(s):
        global _status
        if _spinner is None:
            raise Exception('waitfor has not been called')
        _lock.acquire()
        _status = s
        _lock.release()
        _spinner.update()

    def status_append(s):
        global _status
        if _spinner is None:
            raise Exception('waitfor has not been called')
        _lock.acquire()
        _status += s
        _lock.release()
        _spinner.update()

    def succeeded(s = 'Done'):
        _stop_spinner('[${BOLD}${GREEN}+${NORMAL}]', s)

    def failed(s = 'FAILED!'):
        _stop_spinner('[${BOLD}${RED}-${NORMAL}]', s)

else:
    _message = ''

    def waitfor(s):
        global _message
        _message = s
        _debug(s)

    def status(s):
        status(s, stream=sys.stderr)

    def status_append(s):
        status(s, stream=sys.stderr)

    def succeeded(s = 'Done'):
        success(s, stream=sys.stderr)

    def failed(s = 'FAILED!'):
        fail(s, stream=sys.stderr)


if __name__ == '__main__':
    waitfor("Waiting...")
    time.sleep(1)
    status("Status update")
    time.sleep(1)
    status_append("Status append")
    time.sleep(1)
    succeeded()

    waitfor("Doing some things")
    time.sleep(1)
    failed()
