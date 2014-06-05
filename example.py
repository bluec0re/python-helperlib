from helperlib.logging import default_config
from helperlib.exception import install_hook
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

raise ValueError(123)
spinner.failed()
