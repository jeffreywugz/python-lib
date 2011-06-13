#!/usr/bin/python2
'''
Usages:
  matv.py target rows cols
Examples:
  matv.py 'echo $r $c' 'A B C' 'D E'
'''
import sys
import os
import string
from subprocess import Popen, PIPE, STDOUT

def sub(tpl, **kw):
    return string.Template(tpl).safe_substitute(kw)

def popen(cmd):
    return Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0]

def mesh(rows, cols):
    return [[(r,c) for c in cols] for r in rows]

def map2d(func, mat):
    return [[func(c) for c in r] for r in mat]

def map_mesh(cell, rows, cols):
    return map2d(cell, mesh(rows, cols))

def mat_render(mat):
    return '\n'.join([',\t'.join(map(str, r)) for r in mat])

def mat_add_header(mat, rows, cols):
    return [['X'] + list(cols)] + map(lambda h, r: [h]+list(r), rows, mat)

def mat_sh(cmd, rows, cols):
    mat = map_mesh(lambda (r,c): popen(sub(cmd, r=r, c=c)).strip(), rows, cols)
    return mat_render(mat_add_header(mat, rows, cols))

def mat_sh_wrapper(cmd, rows, cols):
    return mat_sh(cmd, rows.split(','), cols.split(','))
    
if __name__ == '__main__':
    if not len(sys.argv) == 4:sys.stderr.write(__doc__)
    else: print mat_sh_wrapper(*sys.argv[1:])
