#!/usr/bin/env python2
"""
hex2bin.py hex-file bin-file
# hex-file format: 0xaa 0xbb
"""
import re
import sys
import binascii
def hex2bin(hexfile, binfile):
    open(binfile, 'w').write(binascii.unhexlify(''.join(re.findall('0x(..)', open(hexfile).read()))))
    return binfile

if len(sys.argv) != 3:
    print __doc__
    sys.exit(1)
hex2bin(sys.argv[1], sys.argv[2])

