#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([cwd])
from common import *

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
    
tasks = get_default_tasks()
[execfile(t, globals()) for t in tasks]
run_cmd(locals(), sys.argv[1:])
    
