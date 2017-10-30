from unittest import TestCase
from helperlib.binary import *

class HexdumpTestCase(TestCase):
    def test_hexdump(self):
        expected = [
            '00: 00 01 02 03 04 05 06 07 ........',
            '08: 08 09 0A 0B 0C 0D 0E 0F ........',
            '10: 10 11 12 13 14 15 16 17 ........',
            '18: 18 19 1A 1B 1C 1D 1E 1F ........',
            '20: 20 21 22 23 24 25 26 27  !"#$%&\'',
            '28: 28 29 2A 2B 2C 2D 2E 2F ()*+,-./',
            '30: 30 31 32 33 34 35 36 37 01234567',
            '38: 38 39 3A 3B 3C 3D 3E 3F 89:;<=>?',
            '40: 40 41 42 43 44 45 46 47 @ABCDEFG',
            '48: 48 49 4A 4B 4C 4D 4E 4F HIJKLMNO',
            '50: 50 51 52 53 54 55 56 57 PQRSTUVW',
            '58: 58 59 5A 5B 5C 5D 5E 5F XYZ[\]^_',
            '60: 60 61 62 63 64 65 66 67 `abcdefg',
            '68: 68 69 6A 6B 6C 6D 6E 6F hijklmno',
            '70: 70 71 72 73 74 75 76 77 pqrstuvw',
            '78: 78 79 7A 7B 7C 7D 7E 7F xyz{|}~.',
            '80: 80 81 82 83 84 85 86 87 ........',
            '88: 88 89 8A 8B 8C 8D 8E 8F ........',
            '90: 90 91 92 93 94 95 96 97 ........',
            '98: 98 99 9A 9B 9C 9D 9E 9F ........',
            'A0: A0 A1 A2 A3 A4 A5 A6 A7 ........',
            'A8: A8 A9 AA AB AC AD AE AF ........',
            'B0: B0 B1 B2 B3 B4 B5 B6 B7 ........',
            'B8: B8 B9 BA BB BC BD BE BF ........',
            'C0: C0 C1 C2 C3 C4 C5 C6 C7 ........',
            'C8: C8 C9 CA CB CC CD CE CF ........',
            'D0: D0 D1 D2 D3 D4 D5 D6 D7 ........',
            'D8: D8 D9 DA DB DC DD DE DF ........',
            'E0: E0 E1 E2 E3 E4 E5 E6 E7 ........',
            'E8: E8 E9 EA EB EC ED EE EF ........',
            'F0: F0 F1 F2 F3 F4 F5 F6 F7 ........',
            'F8: F8 F9 FA FB FC FD FE FF ........',
        ]
        source = bytes([i for i in range(256)])
        dump = list(hexdump("".join(chr(i) for i in source), header=False))
        self.assertListEqual(dump, expected)
        dump = list(hexdump("".join(chr(i) for i in source), header=True))
        self.assertListEqual(dump, ['     0  1  2  3  4  5  6  7'] + expected)
        dump = list(hexdump(source, header=False))
        self.assertListEqual(dump, expected)
        dump = list(hexdump(source, header=True))
        self.assertListEqual(dump, ['     0  1  2  3  4  5  6  7'] + expected)

    def test_parse_hexdump(self):
        source = "\n".join([
            '00: 00 01 02 03 04 05 06 07 ........',
            '08: 08 09 0A 0B 0C 0D 0E 0F ........',
            '10: 10 11 12 13 14 15 16 17 ........',
            '18: 18 19 1A 1B 1C 1D 1E 1F ........',
            '20: 20 21 22 23 24 25 26 27  !"#$%&\'',
            '28: 28 29 2A 2B 2C 2D 2E 2F ()*+,-./',
            '30: 30 31 32 33 34 35 36 37 01234567',
            '38: 38 39 3A 3B 3C 3D 3E 3F 89:;<=>?',
            '40: 40 41 42 43 44 45 46 47 @ABCDEFG',
            '48: 48 49 4A 4B 4C 4D 4E 4F HIJKLMNO',
            '50: 50 51 52 53 54 55 56 57 PQRSTUVW',
            '58: 58 59 5A 5B 5C 5D 5E 5F XYZ[\]^_',
            '60: 60 61 62 63 64 65 66 67 `abcdefg',
            '68: 68 69 6A 6B 6C 6D 6E 6F hijklmno',
            '70: 70 71 72 73 74 75 76 77 pqrstuvw',
            '78: 78 79 7A 7B 7C 7D 7E 7F xyz{|}~.',
            '80: 80 81 82 83 84 85 86 87 ........',
            '88: 88 89 8A 8B 8C 8D 8E 8F ........',
            '90: 90 91 92 93 94 95 96 97 ........',
            '98: 98 99 9A 9B 9C 9D 9E 9F ........',
            'A0: A0 A1 A2 A3 A4 A5 A6 A7 ........',
            'A8: A8 A9 AA AB AC AD AE AF ........',
            'B0: B0 B1 B2 B3 B4 B5 B6 B7 ........',
            'B8: B8 B9 BA BB BC BD BE BF ........',
            'C0: C0 C1 C2 C3 C4 C5 C6 C7 ........',
            'C8: C8 C9 CA CB CC CD CE CF ........',
            'D0: D0 D1 D2 D3 D4 D5 D6 D7 ........',
            'D8: D8 D9 DA DB DC DD DE DF ........',
            'E0: E0 E1 E2 E3 E4 E5 E6 E7 ........',
            'E8: E8 E9 EA EB EC ED EE EF ........',
            'F0: F0 F1 F2 F3 F4 F5 F6 F7 ........',
            'F8: F8 F9 FA FB FC FD FE FF ........',
        ])
        expected = bytes([i for i in range(256)])

        parsed = parse_hexdump(source)
        self.assertEqual(parsed, expected)
        parsed = parse_hexdump('     0  1  2  3  4  5  6  7\n' + source)
        self.assertEqual(parsed, expected)

    def test_folded_hexdump(self):
        source = ('A' * 4 + 'B' * 16 + 'C' * 32 + 'D' * 4).encode()
        expected = [
            '     0  1  2  3  4  5  6  7',
            '00: 41 41 41 41 42 42 42 42 AAAABBBB',
            '    *',
            '10: 42 42 42 42 43 43 43 43 BBBBCCCC',
            '    *',
            '30: 43 43 43 43 44 44 44 44 CCCCDDDD',
        ]

        dump = list(hexdump(source, header=True, folded=True))
        self.assertListEqual(dump, expected)

    def test_parse_folded_hexdump(self):
        expected = ('A' * 4 + 'B' * 16 + 'C' * 32 + 'D' * 4).encode()
        source = '\n'.join([
            '     0  1  2  3  4  5  6  7',
            '00: 41 41 41 41 42 42 42 42 AAAABBBB',
            '    *',
            '10: 42 42 42 42 43 43 43 43 BBBBCCCC',
            '    *',
            '30: 43 43 43 43 44 44 44 44 CCCCDDDD',
        ])

        parsed = parse_hexdump(source)
        self.assertEqual(parsed, expected)

    def test_hexII(self):
        source = bytes([i for i in range(256)])
        expected = [
            '      0  1  2  3  4  5  6  7',
            '000:    01 02 03 04 05 06 07',
            '008: 08 09 0A 0B 0C 0D 0E 0F',
            '010: 10 11 12 13 14 15 16 17',
            '018: 18 19 1A 1B 1C 1D 1E 1F',
            '020: .  .! ." .# .$ .% .& .\'',
            '028: .( .) .* .+ ., .- .. ./',
            '030: .0 .1 .2 .3 .4 .5 .6 .7',
            '038: .8 .9 .: .; .< .= .> .?',
            '040: .@ .A .B .C .D .E .F .G',
            '048: .H .I .J .K .L .M .N .O',
            '050: .P .Q .R .S .T .U .V .W',
            '058: .X .Y .Z .[ .\ .] .^ ._',
            '060: .` .a .b .c .d .e .f .g',
            '068: .h .i .j .k .l .m .n .o',
            '070: .p .q .r .s .t .u .v .w',
            '078: .x .y .z .{ .| .} .~ 7F',
            '080: 80 81 82 83 84 85 86 87',
            '088: 88 89 8A 8B 8C 8D 8E 8F',
            '090: 90 91 92 93 94 95 96 97',
            '098: 98 99 9A 9B 9C 9D 9E 9F',
            '0A0: A0 A1 A2 A3 A4 A5 A6 A7',
            '0A8: A8 A9 AA AB AC AD AE AF',
            '0B0: B0 B1 B2 B3 B4 B5 B6 B7',
            '0B8: B8 B9 BA BB BC BD BE BF',
            '0C0: C0 C1 C2 C3 C4 C5 C6 C7',
            '0C8: C8 C9 CA CB CC CD CE CF',
            '0D0: D0 D1 D2 D3 D4 D5 D6 D7',
            '0D8: D8 D9 DA DB DC DD DE DF',
            '0E0: E0 E1 E2 E3 E4 E5 E6 E7',
            '0E8: E8 E9 EA EB EC ED EE EF',
            '0F0: F0 F1 F2 F3 F4 F5 F6 F7',
            '0F8: F8 F9 FA FB FC FD FE ##',
            '100: ]'
        ]

        dump = list(hexII(source))
        self.assertListEqual(dump, expected)

        source2 = bytes([i for i in range(69)])
        expected2 = [
            '     0  1  2  3  4  5  6  7',
            '00:    01 02 03 04 05 06 07',
            '08: 08 09 0A 0B 0C 0D 0E 0F',
            '10: 10 11 12 13 14 15 16 17',
            '18: 18 19 1A 1B 1C 1D 1E 1F',
            '20: .  .! ." .# .$ .% .& .\'',
            '28: .( .) .* .+ ., .- .. ./',
            '30: .0 .1 .2 .3 .4 .5 .6 .7',
            '38: .8 .9 .: .; .< .= .> .?',
            '40: .@ .A .B .C .D ]',
        ]

        dump = list(hexII(source2))
        self.assertListEqual(dump, expected2)

    def test_parse_hexII(self):
        source = "\n".join([
            '      0  1  2  3  4  5  6  7',
            '000:    01 02 03 04 05 06 07',
            '008: 08 09 0A 0B 0C 0D 0E 0F',
            '010: 10 11 12 13 14 15 16 17',
            '018: 18 19 1A 1B 1C 1D 1E 1F',
            '020: .  .! ." .# .$ .% .& .\'',
            '028: .( .) .* .+ ., .- .. ./',
            '030: .0 .1 .2 .3 .4 .5 .6 .7',
            '038: .8 .9 .: .; .< .= .> .?',
            '040: .@ .A .B .C .D .E .F .G',
            '048: .H .I .J .K .L .M .N .O',
            '050: .P .Q .R .S .T .U .V .W',
            '058: .X .Y .Z .[ .\ .] .^ ._',
            '060: .` .a .b .c .d .e .f .g',
            '068: .h .i .j .k .l .m .n .o',
            '070: .p .q .r .s .t .u .v .w',
            '078: .x .y .z .{ .| .} .~ 7F',
            '080: 80 81 82 83 84 85 86 87',
            '088: 88 89 8A 8B 8C 8D 8E 8F',
            '090: 90 91 92 93 94 95 96 97',
            '098: 98 99 9A 9B 9C 9D 9E 9F',
            '0A0: A0 A1 A2 A3 A4 A5 A6 A7',
            '0A8: A8 A9 AA AB AC AD AE AF',
            '0B0: B0 B1 B2 B3 B4 B5 B6 B7',
            '0B8: B8 B9 BA BB BC BD BE BF',
            '0C0: C0 C1 C2 C3 C4 C5 C6 C7',
            '0C8: C8 C9 CA CB CC CD CE CF',
            '0D0: D0 D1 D2 D3 D4 D5 D6 D7',
            '0D8: D8 D9 DA DB DC DD DE DF',
            '0E0: E0 E1 E2 E3 E4 E5 E6 E7',
            '0E8: E8 E9 EA EB EC ED EE EF',
            '0F0: F0 F1 F2 F3 F4 F5 F6 F7',
            '0F8: F8 F9 FA FB FC FD FE ##',
            '100: ]'
        ])
        expected = bytes([i for i in range(256)])

        parsed = parse_hexII(source)
        self.assertEqual(parsed, expected)

        source2 = "\n".join([
            '000:       02 03 04 05 06 07',
            '008: 08 09 0A 0B 0C 0D 0E 0F',
            '010: 10 11 12 13 14 15 16 17',
            '018: 18 19 1A 1B 1C 1D 1E 1F',
            '020: .  .! ." .# .$ .% .& .\'',
            '028: .( .) .* .+ ., .- .. ./',
            '030: .0 .1 .2 .3 .4 .5 .6 .7',
            '038: .8 .9 .: .; .< .= .> .?',
            '040: .@ .A .B .C .D .E .F .G',
            '048: .H .I .J .K .L .M .N .O',
            '050: .P .Q .R .S .T .U .V .W',
            '058: .X .Y .Z .[ .\ .] .^ ._',
            '060: .` .a .b .c .d .e .f .g',
            '068: .h .i .j .k .l .m .n .o',
            '070: .p .q .r .s .t .u .v .w',
            '078: .x .y .z .{ .| .} .~ 7F',
            '080: 80 81 82 83 84 85 86 87',
            '088: 88 89 8A 8B 8C 8D 8E 8F',
            '090: 90 91 92 93 94 95 96 97',
            '098: 98 99 9A 9B 9C 9D 9E 9F',
            '0A0: A0 A1 A2 A3 A4 A5 A6 A7',
            '0A8: A8 A9 AA AB AC AD AE AF',
            '0B0: B0 B1 B2 B3 B4 B5 B6 B7',
            '0B8: B8 B9 BA BB BC BD BE BF',
            '0C0: C0 C1 C2 C3 C4 C5 C6 C7',
            '0C8: C8 C9 CA CB CC CD CE CF',
            '0D0: D0 D1 D2 D3 D4 D5 D6 D7',
            '0D8: D8 D9 DA DB DC DD DE DF',
            '0E0: E0 E1 E2 E3 E4 E5 E6 E7',
            '0E8: E8 E9 EA EB EC ED EE EF',
            '0F0: F0 F1 F2 F3 F4 F5 F6 F7',
            '0F8: F8 F9 FA FB FC FD FE ##',
            '100: ]'
        ])
        expected2 = bytes([0, 0] + [i for i in range(2, 256)])

        parsed = parse_hexII(source2)
        self.assertEqual(parsed, expected2)

    def test_folded_hexII(self):
        source = ('A' * 4 + 'B' * 16 + 'C' * 32 + 'D' * 4).encode()
        expected = [
            '     0  1  2  3  4  5  6  7',
            '00: .A .A .A .A .B .B .B .B',
            '    *',
            '10: .B .B .B .B .C .C .C .C',
            '    *',
            '30: .C .C .C .C .D .D .D .D',
            '38: ]',
        ]

        dump = list(hexII(source, header=True, folded=True))
        self.assertListEqual(dump, expected)

    def test_parse_folded_hexII(self):
        expected = ('A' * 4 + 'B' * 16 + 'C' * 32 + 'D' * 4).encode()
        source = '\n'.join([
            '     0  1  2  3  4  5  6  7',
            '00: .A .A .A .A .B .B .B .B',
            '    *',
            '10: .B .B .B .B .C .C .C .C',
            '    *',
            '30: .C .C .C .C .D .D .D .D',
            '38: ]',
        ])

        parsed = parse_hexII(source)
        self.assertEqual(parsed, expected)
