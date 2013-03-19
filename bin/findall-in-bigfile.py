#!/usr/bin/env python2
"""
findall.py pat input-file
"""

import sys
import re
import mmap

def find_all(path, pat):
    with open(path, "r") as f:
        return re.findall(pat, mmap.mmap(f.fileno(), 0, mmap.MAP_PRIVATE, mmap.PROT_READ), re.M)
def tolist(x):
    if type(x) == list or type(x) == tuple:
        return x
    else:
        return [x]
if len(sys.argv) != 3:
    print __doc__
else:
    for i in find_all(sys.argv[2], sys.argv[1]):
        print ' '.join(tolist(i))
        
