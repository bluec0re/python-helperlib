from __future__ import absolute_import, print_function, unicode_literals

import sys
import struct
from string import punctuation, digits, ascii_letters

import six

from .internal import TERM


def hexdump(data, cols=8, folded=False, stream=False, offset=0, header=False):
    """
    yields the rows of the hex dump

    Arguments:
        data -- data to dump
        cols -- number of octets per row
        folded -- fold long ranges of equal bytes
        stream -- dont use len on data

    >>> from string import ascii_uppercase
    >>> print('\\n'.join(hexdump("".join(chr(i) for i in range(256)))))
    00: 00 01 02 03 04 05 06 07 ........
    08: 08 09 0A 0B 0C 0D 0E 0F ........
    10: 10 11 12 13 14 15 16 17 ........
    18: 18 19 1A 1B 1C 1D 1E 1F ........
    20: 20 21 22 23 24 25 26 27  !"#$%&'
    28: 28 29 2A 2B 2C 2D 2E 2F ()*+,-./
    30: 30 31 32 33 34 35 36 37 01234567
    38: 38 39 3A 3B 3C 3D 3E 3F 89:;<=>?
    40: 40 41 42 43 44 45 46 47 @ABCDEFG
    48: 48 49 4A 4B 4C 4D 4E 4F HIJKLMNO
    50: 50 51 52 53 54 55 56 57 PQRSTUVW
    58: 58 59 5A 5B 5C 5D 5E 5F XYZ[\]^_
    60: 60 61 62 63 64 65 66 67 `abcdefg
    68: 68 69 6A 6B 6C 6D 6E 6F hijklmno
    70: 70 71 72 73 74 75 76 77 pqrstuvw
    78: 78 79 7A 7B 7C 7D 7E 7F xyz{|}~.
    80: 80 81 82 83 84 85 86 87 ........
    88: 88 89 8A 8B 8C 8D 8E 8F ........
    90: 90 91 92 93 94 95 96 97 ........
    98: 98 99 9A 9B 9C 9D 9E 9F ........
    A0: A0 A1 A2 A3 A4 A5 A6 A7 ........
    A8: A8 A9 AA AB AC AD AE AF ........
    B0: B0 B1 B2 B3 B4 B5 B6 B7 ........
    B8: B8 B9 BA BB BC BD BE BF ........
    C0: C0 C1 C2 C3 C4 C5 C6 C7 ........
    C8: C8 C9 CA CB CC CD CE CF ........
    D0: D0 D1 D2 D3 D4 D5 D6 D7 ........
    D8: D8 D9 DA DB DC DD DE DF ........
    E0: E0 E1 E2 E3 E4 E5 E6 E7 ........
    E8: E8 E9 EA EB EC ED EE EF ........
    F0: F0 F1 F2 F3 F4 F5 F6 F7 ........
    F8: F8 F9 FA FB FC FD FE FF ........

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
        hexlen = len(hex(offset + size - 1)) - 2
        offset_fmt = '{{:0{}X}}: '.format(hexlen)
        if header:
            line = ' ' * (hexlen + 2)
            for i in range(min(cols, size + offset)):
                line += '{:2X} '.format(i)
            yield line
    else:
        size = None
        hexlen = 5
        offset_fmt = '{:05X}: '
        if header:
            line = ' ' * (5 + 2)
            for i in range(cols):
                line += '{:2X} '.format(i)
            yield line

    # convert input into iter if needed
    if hasattr(data, 'read'):
        def _tmp():
            return data.read(1)
        data_iter = iter(_tmp, '')
    else:
        data_iter = iter(data)

    run = True
    while run:
        line = offset_fmt.format(offset - (offset % cols))
        # ASCII dump
        string = ''
        skipped = 0
        prefix = (offset % cols)

        # padding
        if offset % cols != 0:
            line += '   ' * prefix
            string += ' ' * prefix

        try:
            for _ in range(cols - (offset % cols)):
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
                    yield ' ' * (hexlen + 2) + '*'
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


def print_hexdump(data, colored=False, cols=16, file=sys.stdout, header=False, *args, **kwargs):
    first = header
    for row in hexdump(data, cols, header=header, *args, **kwargs):
        if colored:
            if first:
                row = TERM.render("${CYAN}" + row + "${NORMAL}")
                first = False
            else:
                idx = row.find(':') + 1
                row = TERM.render("${CYAN}" + row[:idx] + "${YELLOW}" + row[idx:idx+3*cols] + "${BLUE}") + row[idx+3*cols:] + TERM.render("${NORMAL}")
        print(row, file=file)


def hexII(data, cols=8, folded=False, stream=False, offset=0, header=True):
    ASCII = (punctuation + digits + ascii_letters).encode()

    def char(c):
        if c == 0x00:
            return '  '

        if c == 0xFF:
            return '##'

        if c in ASCII:
            return '.' + chr(c)

        return '{:02X}'.format(c)

    last_byte = None
    fold = False

    # determine index width
    if not stream:
        size = len(data)
        hexlen = len(hex(offset + size - 1)) - 2
        offset_fmt = '{{:0{}X}}: '.format(hexlen)
        if header:
            line = ' ' * (hexlen + 2)
            for i in range(min(cols, size + offset)):
                line += '{:2X} '.format(i)
            yield line
    else:
        size = None
        hexlen = 5
        offset_fmt = '{:05X}: '
        if header:
            line = ' ' * (5 + 2)
            for i in range(cols):
                line += '{:2X} '.format(i)
            yield line


    # convert input into iter if needed
    if hasattr(data, 'read'):
        def _tmp():
            return data.read(1)
        data_iter = iter(_tmp, '')
    else:
        data_iter = iter(data)

    run = True
    while run:
        line = offset_fmt.format(offset - (offset % cols))
        skipped = 0
        prefix = (offset % cols)

        # padding
        if offset % cols != 0:
            line += '   ' * prefix

        try:
            for _ in range(cols - (offset % cols)):
                byte = next(data_iter)
                # byte is equal to previous => count range of equal bytes
                if last_byte == byte:
                    skipped += 1
                offset += 1
                line += char(byte) + ' '
                last_byte = byte
        except StopIteration:
            run = False

        # if folding is requested
        if folded:
            # all bytes are equal to the last byte of the previous block
            if skipped == cols:
                # show * the first time
                if not fold:
                    yield ' ' * (hexlen + 2) + '*'
                fold = True
                continue
            else:
                fold = False

        # padding
        if offset % cols != 0:
            line += '   ' * (cols - (offset % cols))

        # yield only if no StopIteration was thrown or bytes are remaining
        if offset % cols != 0 or run:
            yield line


def print_hexII(data, colored=False, cols=16, file=sys.stdout, *args, **kwargs):
    for row in hexII(data, cols, *args, **kwargs):
        if False and colored:
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


class StructField:
    '''
    Descriptor representing a simple structure field
    '''
    def __init__(self, format, offset):
        self.format = format
        self.offset = offset

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            r = struct.unpack_from(
                    self.format,
                    instance._buffer,
                    self.offset
            )

        return r[0] if len(r) == 1 else r

    def __set__(self, instance, values):
        if instance is None:
            return

        if not isinstance(values, (list,tuple)):
            values = [values]

        struct.pack_into(
            self.format,
            instance._buffer,
            self.offset,
            *values
        )

    def __repr__(self):
        return '{}(format={!r}, offset={!r})'.format(type(self).__name__, self.format, self.offset)


class VariableStructField(StructField):
    def __init__(self, format, offset, length_field):
        super(VariableStructField, self).__init__(format, offset)
        self.length_field = length_field

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            length = getattr(instance, self.length_field)
            self.format = "{0}{1}{2}".format(
                self.format[0],
                length,
                self.format[1:]
            )
            missing = struct.calcsize(self.format) + self.offset - len(instance._buffer)
            if missing > 0:
                raise IOError('Requires {} additional bytes'.format(missing))
            return super(VariableStructField, self).__get__(instance, cls)

    def __set__(self, instance, value):
        if instance is None:
            return

        length = len(value)
        length2 = getattr(instance, self.length_field)
        if length != length2:
            raise ValueError('Different lengths for length field ({} vs {})'.format(length, length2))
        # setattr(instance, self.length_field, length)
        self.format = "{0}{1}{2}".format(
            self.format[0],
            length,
            self.format[-1]
        )
        super(VariableStructField, self).__set__(instance, value)


class NestedStruct:
    '''
    Descriptor representing a nested structure
    '''
    def __init__(self, name, struct_type, offset):
        self.name = name
        self.struct_type = struct_type
        self.offset = offset

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            data = instance._buffer[
                self.offset:
                self.offset + self.struct_type._dynamic_struct_size()
            ]
            result = self.struct_type(data)
            # Save resulting structure back on instance to avoid
            # further recomputation of this step
            setattr(instance, self.name, result)
            return result


class StructureMeta(type):
    '''
    Metaclass that automatically creates StructField descriptors
    '''
    def __init__(self, clsname, bases, clsdict):
        fields = getattr(self, '_fields_', [])
        byte_order = ''
        offset = 0
        for field in fields:
            length_field = None
            if len(field) == 3:
                format, fieldname, length_field = field
            else:
                format, fieldname = field

            if isinstance(format, StructureMeta):
                setattr(self, fieldname,
                        NestedStruct(fieldname, format, offset))
                offset += format.struct_size
            else:
                if format.startswith(('<', '>', '!', '@')):
                    byte_order = format[0]
                    format = format[1:]
                format = byte_order + format
                if length_field:
                    setattr(self, fieldname, VariableStructField(format, offset, length_field))
                else:
                    setattr(self, fieldname, StructField(format, offset))
                offset += struct.calcsize(format)
            setattr(self, 'struct_size', offset)

    def __str__(self):
        lines = [
                '{0}(0x{1:x}, {1}):'.format(type(self).__name__, self.struct_size)
        ]

        for field in getattr(self, '_fields_', []):
            lines.append('  0x{0:02x} {0:3}: {1}'.format(
                    getattr(self, field[1]).offset,
                    field[1]
                )
            )

        return '\n'.join(lines)

    def _dynamic_struct_size(self):
        size = 0
        for data in getattr(self, '_fields_', []):
            format, field = data[:2]
            field = getattr(self, field)
            # TODO: calc dynamic size
            if False: #hasattr(field, 'struct_size'):
                size += field._dynamic_struct_size()
            elif hasattr(format, 'struct_size'):
                size += format.struct_size
            else:
                size += struct.calcsize(format)

        return size


@six.add_metaclass(StructureMeta)
class Structure():
    def __init__(self, bytedata=None):
        if bytedata is None:
            bytedata = bytearray(self.struct_size)
        elif isinstance(bytedata, int):
            bytedata = bytearray(bytedata)
        if not isinstance(bytedata, memoryview):
            bytedata = memoryview(bytedata)
        self._buffer = bytedata

    def __repr__(self):
        fields = getattr(self, '_fields_', [])
        attrs = ['{}={!r}'.format(f[1], getattr(self, f[1])) for f in fields]
        return '{}({})'.format(type(self).__name__, ', '.join(attrs))

    @classmethod
    def from_file(cls, f, additional=0):
        return cls(f.read(cls.struct_size + additional))

    @property
    def raw_bytes(self):
        return bytes(self._buffer)

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

