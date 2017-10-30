#!/usr/bin/env python
# -*- coding: utf-8 -*-
from helperlib.binary import print_hexdump
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('FILE', nargs='?', type=argparse.FileType('rb'))
parser.add_argument('-H', '--header', action='store_true')
parser.add_argument('-C', '--color', action='store_true')
parser.add_argument('-c', '--columns', type=int, default=8)
parser.add_argument('-f', '--fold', action='store_true')

args = parser.parse_args()

if not args.FILE:
    fp = sys.stdin.buffer
else:
    fp = args.FILE


print_hexdump(
        fp.read(),
        header=args.header,
        colored=args.color,
        cols=args.columns,
        folded=args.fold
        )
