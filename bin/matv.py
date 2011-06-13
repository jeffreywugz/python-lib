#!/usr/bin/python2
'''
Usages:
  matv.py target rows cols
Examples:
  matv.py 'echo $r $c' 'A B C' 'D E'
'''
import sys, os
import re, string
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

def mat_render(mat, sep=',\t'):
    sep = sep.replace('\\t', '\t')
    return '\n'.join([sep.join(map(str, r)) for r in mat])

def mat_add_header(mat, rows, cols):
    return [['X'] + list(cols)] + map(lambda h, r: [h]+list(r), rows, mat)

def mat_sh(cmd, rows, cols, sep='\t'):
    def cmd_part(t):
        return re.sub('\[.*?\]', '', t)
    def header_part(t): 
        m = re.search('\[(.*?)\]', t)
        return m and m.group(1) or t
    mat = map_mesh(lambda (r,c): popen(sub(cmd, r=cmd_part(r), c=cmd_part(c))).strip(), rows, cols)
    return mat_render(mat_add_header(mat, map(header_part, rows), map(header_part, cols)), sep)

def mat_sh_wrapper(cmd, rows, cols, sep='\t'):
    return mat_sh(cmd, rows.split(','), cols.split(','), sep=sep)
    
if __name__ == '__main__':
    if len(sys.argv) == 4 or len(sys.argv) == 5: print mat_sh_wrapper(*sys.argv[1:])
    else: sys.stderr.write(__doc__)
