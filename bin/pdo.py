#!/usr/bin/python

"""
pdo which means `pattern do', can be use to do some operation based on a seqence of strings
Usage: pdo '$base.png' echo '$base.jpg' : *.png
"""
import sys
import os, os.path
import exceptions
from common import *
import traceback
import string, re

class PdoException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'PdoException(%s, %s)'%(repr(self.msg), repr(self.obj))
    
def parse(args):
    def get_colon_index(args):
        for i,v in enumerate(args):
            if v.startswith(':'): return i
        raise PdoException('Missing ":" in args', args)
    def split_by_colon(args):
        i = get_colon_index(args)
        return args[:i], args[i+1:]
    head, items = split_by_colon(args)
    if not head: raise PdoException('Missing pattern before ":"', head)
    pat, cmd = head[0], head[1:]
    return pat, cmd, items

def pdo_run(args):
    pat, cmd, items = parse(args)
    cmd =  ' '.join(cmd)
    for i in items:
        env = str2dict(pat, i)
        _cmd = sub(cmd, env)
        shell(_cmd)
        
def main(args):
    try:
        pdo_run(args)
    except PdoException as e:
        print(e)
        print(globals()['__doc__'])
    except exceptions.Exception as e:
        print("Internal Error")
        print(traceback.format_exc())
        return

if __name__ == '__main__':
    main(sys.argv[1:])
