from __future__ import absolute_import, print_function, unicode_literals

import sys

from .internal import TERM


def hexdump(data, cols=8, folded=False, stream=False):
    """
    yields the rows of the hex dump

    Arguments:
        data -- data to dump
        cols -- number of octets per row
        folded -- fold long ranges of equal bytes
        stream -- dont use len on data

    >>> from string import ascii_uppercase
    >>> print('\\n'.join(hexdump("".join(chr(i) for i in range(256)))))
    000: 00 01 02 03 04 05 06 07 ........
    008: 08 09 0A 0B 0C 0D 0E 0F ........
    010: 10 11 12 13 14 15 16 17 ........
    018: 18 19 1A 1B 1C 1D 1E 1F ........
    020: 20 21 22 23 24 25 26 27  !"#$%&'
    028: 28 29 2A 2B 2C 2D 2E 2F ()*+,-./
    030: 30 31 32 33 34 35 36 37 01234567
    038: 38 39 3A 3B 3C 3D 3E 3F 89:;<=>?
    040: 40 41 42 43 44 45 46 47 @ABCDEFG
    048: 48 49 4A 4B 4C 4D 4E 4F HIJKLMNO
    050: 50 51 52 53 54 55 56 57 PQRSTUVW
    058: 58 59 5A 5B 5C 5D 5E 5F XYZ[\]^_
    060: 60 61 62 63 64 65 66 67 `abcdefg
    068: 68 69 6A 6B 6C 6D 6E 6F hijklmno
    070: 70 71 72 73 74 75 76 77 pqrstuvw
    078: 78 79 7A 7B 7C 7D 7E 7F xyz{|}~.
    080: 80 81 82 83 84 85 86 87 ........
    088: 88 89 8A 8B 8C 8D 8E 8F ........
    090: 90 91 92 93 94 95 96 97 ........
    098: 98 99 9A 9B 9C 9D 9E 9F ........
    0A0: A0 A1 A2 A3 A4 A5 A6 A7 ........
    0A8: A8 A9 AA AB AC AD AE AF ........
    0B0: B0 B1 B2 B3 B4 B5 B6 B7 ........
    0B8: B8 B9 BA BB BC BD BE BF ........
    0C0: C0 C1 C2 C3 C4 C5 C6 C7 ........
    0C8: C8 C9 CA CB CC CD CE CF ........
    0D0: D0 D1 D2 D3 D4 D5 D6 D7 ........
    0D8: D8 D9 DA DB DC DD DE DF ........
    0E0: E0 E1 E2 E3 E4 E5 E6 E7 ........
    0E8: E8 E9 EA EB EC ED EE EF ........
    0F0: F0 F1 F2 F3 F4 F5 F6 F7 ........
    0F8: F8 F9 FA FB FC FD FE FF ........

    >>> print('\\n'.join(hexdump(ascii_uppercase)))
    00: 41 42 43 44 45 46 47 48 ABCDEFGH
    08: 49 4A 4B 4C 4D 4E 4F 50 IJKLMNOP
    10: 51 52 53 54 55 56 57 58 QRSTUVWX
    18: 59 5A                   YZ
    >>> print('\\n'.join(hexdump(ascii_uppercase, stream=True)))
    00000: 41 42 43 44 45 46 47 48 ABCDEFGH
    00008: 49 4A 4B 4C 4D 4E 4F 50 IJKLMNOP
    00010: 51 52 53 54 55 56 57 58 QRSTUVWX
    00018: 59 5A                   YZ
    >>> print('\\n'.join(hexdump(ascii_uppercase + "0"*256, folded=True)))
    000: 41 42 43 44 45 46 47 48 ABCDEFGH
    008: 49 4A 4B 4C 4D 4E 4F 50 IJKLMNOP
    010: 51 52 53 54 55 56 57 58 QRSTUVWX
    018: 59 5A 30 30 30 30 30 30 YZ000000
    *
    118: 30 30                   00
    >>> print('\\n'.join(hexdump(ascii_uppercase + "0"*256, folded=True, stream=True)))
    00000: 41 42 43 44 45 46 47 48 ABCDEFGH
    00008: 49 4A 4B 4C 4D 4E 4F 50 IJKLMNOP
    00010: 51 52 53 54 55 56 57 58 QRSTUVWX
    00018: 59 5A 30 30 30 30 30 30 YZ000000
    *
    00118: 30 30                   00
    >>> print('\\n'.join(hexdump(ascii_uppercase, cols=16)))
    00: 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 50 ABCDEFGHIJKLMNOP
    10: 51 52 53 54 55 56 57 58 59 5A                   QRSTUVWXYZ
    """
    last_byte = None
    fold = False

    # determine index width
    if not stream:
        size = len(data)
        offset_fmt = '{{:0{}X}}: '.format(len(hex(size))-2)
    else:
        size = None
        offset_fmt = '{:05X}: '

    # convert input into iter if needed
    if hasattr(data, 'read'):
        def _tmp():
            return data.read(1)
        data_iter = iter(_tmp, '')
    else:
        data_iter = iter(data)

    offset = 0
    run = True
    while run:
        line = offset_fmt.format(offset)
        # ASCII dump
        string = ''
        skipped = 0
        try:
            for i in range(cols):
                byte = next(data_iter)
                # byte is equal to previous => count range of equal bytes
                if last_byte == byte:
                    skipped += 1
                offset += 1
                if isinstance(byte, str):
                    bval = ord(byte)
                elif isinstance(byte, int):
                    bval = byte
                    if 31 < bval < 127:
                        byte = chr(bval)
                else:
                    bval = list(byte)[0]
                    if 31 < bval < 127:
                        byte = chr(bval)

                if 31 < bval < 127:
                    string += byte
                else:
                    string += '.'
                line += '{:02X} '.format(bval)
                last_byte = byte
        except StopIteration:
            run = False

        # if folding is requested
        if folded:
            # all bytes are equal to the last byte of the previous block
            if skipped == cols:
                # show * the first time
                if not fold:
                    yield '*'
                fold = True
                continue
            else:
                fold = False

        # padding
        if offset % cols != 0:
            line += '   ' * (cols - (offset % cols))

        # yield only if no StopIteration was thrown or bytes are remaining
        if offset % cols != 0 or run:
            line += string
            yield line


def print_hexdump(data, colored=False, cols=8, file=sys.stdout, *args, **kwargs):
    for row in hexdump(data, cols, *args, **kwargs):
        if colored:
            idx = row.find(':') + 1
            row = TERM.render("${CYAN}" + row[:idx] + "${YELLOW}" + row[idx:idx+3*cols] + "${BLUE}") + row[idx+3*cols:] + TERM.render("${NORMAL}")
        print(row, file=file)


def print_struct(struct, ident=0):
    """
    >>> from ctypes import *
    >>> class Test(Structure):
    ...     _fields_ = [('foo', c_int)]
    ... 
    >>> class Test2(Structure):
    ...     _fields_ = [('foo', Test), ('bar', c_int)]
    ... 
    >>> t = Test2()
    >>> t.foo.foo = 2
    >>> t.bar = 1
    >>> print_struct(t)
    foo: 
     foo: 2
    bar: 1
    """
    if not isinstance(struct, (str, bytes, list, tuple)) and hasattr(struct, '__getitem__'): # array
        print('[')
        for item in struct:
            print(" "*ident, end=' ')
            print_struct(item, ident+1)
        print(" "*ident + "]")
    elif not hasattr(struct, '_fields_'):
        print(struct)
    else:
        if ident:
            print()

        for name, _ in struct._fields_:
            print(" "*ident + "{}:".format(name), end=' ')
            print_struct(getattr(struct, name), ident+1)


if __name__ == '__main__':
    import doctest
    import argparse
    doctest.testmod()


    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', type=argparse.FileType('rb'), nargs='?')
    parser.add_argument('-c', '--color', action='store_true')
    parser.add_argument('-f', '--fold', action='store_true')
    parser.add_argument('-s', '--stream', action='store_true')
    parser.add_argument('-o', '--octets', type=int, default=8)

    args = parser.parse_args()

    if args.FILE:
        fp = args.FILE
    else:
        fp = sys.stdin

    if not args.stream:
        fp = fp.read()

    print_hexdump(fp, cols=args.octets, colored=args.color, folded=args.fold, stream=args.stream)
