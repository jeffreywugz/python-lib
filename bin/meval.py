#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.join(cwd, '..')])
from common import *
import algo, shell, vgen

def get_default_tasks():
    top_tasks = ['top.py', '../top.py', '../../top.py'] 
    local_tasks = ['task.py', '../task.py', '../../task.py']
    try:
        top_index = [os.path.exists(f) for f in top_tasks].index(True)
    except exceptions.ValueError:
        top_index = 0
    tasks = local_tasks[:top_index+1] + top_tasks[:top_index+1]
    tasks.reverse()
    return filter(os.path.exists, tasks)

def echo(*args, **kw_args):
    print 'args=%s, kw_args=%s'%(args, kw_args)

def eval_expr(expr):
    result = eval(expr)
    print result
    
tasks = get_default_tasks()
print 'total tasks: %s'%tasks
for t in tasks:
    print 'load %s'%t
    execfile(t, globals())
run_cmd(locals(), sys.argv[1:])
    
