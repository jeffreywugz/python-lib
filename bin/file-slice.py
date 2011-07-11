#!/usr/bin/python2

"""
Usages:
file-slice.py path start
"""
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write(__doc__)
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        f.seek(int(sys.argv[2]))
        sys.stdout.write(f.read())
