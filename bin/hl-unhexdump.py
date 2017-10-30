#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helperlib.binary import parse_hexdump
import sys


if len(sys.argv) > 1:
    fp = open(sys.argv[1], 'r')
else:
    fp = sys.stdin


sys.stdout.buffer.write(parse_hexdump(fp.read()))
