#!/usr/bin/python2

import sys
import exceptions
from common import *
import traceback

class DFExp(exceptions.Exception):
    def __init__(self, msg, obj):
        self.msg, self.obj = msg, obj
    
    def __str__(self):
        return "DFExp(%s, %s)"%(repr(self.msg), repr(self.obj))

def _print(msg):
    print msg

class DF(object):
    """ DF means `dynamic function':
    + common to a normal function: it is callable.
    + differences: it is composed by a set of normal functions. when it is called, one function will be actually selected.
    Usage: see `df_test()' below.
    """
    def __init__(self, info=_print):
        self.fs = []
        self.info = info

    def reg(self, f):
        if not callable(f): raise DFExp('object is not callable',  f)
        self.fs.append(f)
        return self

    def log(self, msg):
        if callable(self.info): return self.info(msg)

    def call(self, **kw):
        self.log('f(**%s)'%(kw))
        for f in self.fs:
            r = f(self, **kw)
            if r != None:
                self.log('f => %s'% r)
                return r
        self.log('f => None')
        
    def __call__(self, **kw):
        return self.call(**kw)

    def safe_call(self, **kw):
        try:
            return self.call(**kw)
        except exceptions.Exception,e:
            print e
            return None
        
    def __lshift__(self, f):
        return self.reg(f)

def df_test():
    f = DF()
    def add(f, op=None, x=0, y=0, **kw):
        if op == 'add': return x+y
    def mul(f, op=None, x=0, y=0, **kw):
        if op == 'mul': return x*y
    f << add << mul
    print f(op='add', x=2, y=3) # 5
    print f(op='mul', x=2, y=3) # 6


def df_match(proto, args):
    if dict_match(args, **proto): return args
    else: return {}

def df_prepare(self, deps, args):
    return dict(dict_map(lambda dep: self(**dict(args, **dep)), deps), **args)
    
def mkf(match, proto, prepare, deps, action, static):
    def f(self, **in_args):
        _in_args = match(proto, in_args)
        if not _in_args: return None
        act_args = prepare(self, deps, _in_args)
        return action(**dict(static, **act_args))
    return f

if __name__ == '__main__':
    df_test()
