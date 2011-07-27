#!/usr/bin/env python2
'''
./textable.py file sep
'''
import sys
import re

if len(sys.argv) == 1 or len(sys.argv) > 3:
    print __doc__
    sys.exit(1)
txt_file = sys.argv[1]
if len(sys.argv) == 3:
    sep = sys.argv[2]
else:
    sep = ' +'
    
if txt_file == '-':
    fd = sys.stdin
else:
    fd = open(txt_file) 
lines = fd.readlines()
table = ''.join(['%s \\\\ \hline \n'%('& '.join(re.split(sep, line.strip()))) for line in lines])
print table


