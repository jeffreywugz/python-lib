#!/usr/bin/env python2
"""
findall.py pat <input-file
"""

import sys
import re

def tolist(x):
    if type(x) == list or type(x) == tuple:
        return x
    else:
        return [x]
if len(sys.argv) != 2:
    print __doc__
else:
    for i in re.findall(sys.argv[1], sys.stdin.read()):
        print ' '.join(tolist(i))
        
