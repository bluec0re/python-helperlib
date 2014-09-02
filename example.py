from helperlib.logging import default_config
from helperlib.exception import install_hook
from helperlib.terminal import Table, ProgressBar, TerminalController
from helperlib import *
import logging
import time

default_config(level='DEBUG')
install_hook()

logging.debug('test')
logging.info('test')
logging.warning('test')
logging.error('test')

info("Pending....")
done()

x = prompt("Input")
success(x)

spinner.waitfor("Doing long running stuff")
time.sleep(3)
spinner.status("Almost done")
time.sleep(2)
spinner.succeeded()

try:
    raise ValueError(123)
except:
    exc("Catched")
spinner.waitfor("Doing long running stuff")
time.sleep(3)
spinner.failed()

term = TerminalController()
print(term.render("${RED}Some ${MAGENTA}nice${NORMAL} ${BG_GREEN}color${NORMAL} ${BLINK}${CYAN}output${NORMAL}"))


pbar = ProgressBar(term, 'Nice Progressbar is loading...')
pbar.update(0.1, 'wait for it...')
time.sleep(1)
pbar.update(0.5, 'wait for it...!')
time.sleep(1)
pbar.update(1, 'DONE!!!')


tbl = Table(term, [['Linux', 'Rulez'], ['Windows', 'Fails'], ['OS X', 'Sucks']], 'cc', ' | ', True)

tbl.render()
raise ValueError(123)





