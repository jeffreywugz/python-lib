#!/usr/bin/env python2
"""
rep.py template substitute target
"""

import sys
import re

def read(path):
    with open(path) as f:
        return f.read()

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
        
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print __doc__
    else:
        tpl, sub, target = sys.argv[1:]
        write(target, read(tpl) % read(sub))
        
