#!/usr/bin/python

import copy
import sys
from common import *
import config
import vgen

def eval_file(name):
    return execfile(name, globals(), locals())

def eval_expr(expr):
    return eval(expr, globals(), locals())

def crun(expr, *env):
    return map(shell, envsmap(lambda x:msub(expr, **x), *env))
    
if __name__ == '__main__':
    execfile(sys.argv[1], globals())
    mos.cmd_run(locals(), sys.argv[2:])
    
