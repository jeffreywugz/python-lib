#!/usr/bin/python

import sys
import exceptions
from common import *
import traceback
import pprint
import copy

class ManyCallException(exceptions.Exception):
    def __init__(self, msg, obj):
        self.msg, self.obj = msg, obj
    
    def __str__(self):
        return "ManyCallException: %s: %s"%(self.msg, self.obj)

class LMException(exceptions.Exception):
    def __init__(self, msg, obj):
        self.msg, self.obj = msg, obj
    
    def __str__(self):
        return "LMException: %s: %s"%(self.msg, self.obj)

def dict_updated(d, extra={}, **kw):
    new_dict = copy.copy(d)
    new_dict.update(extra, **kw)
    return new_dict

class ManyCall(object):
    def __init__(self):
        self.funcs = []

    def reg(self, func):
        if not callable(func):
            raise ManyCallException('object is not callable',  func)
        self.funcs.append(func)

    def call(self, _many_call_debug_=False, **kw):
        result = {}
        for f in self.funcs:
            try:
                if _many_call_debug_: print 'many call debug: func %s: args %s'%(f, kw)
                updates = f(_many_call_debug_=_many_call_debug_, **kw)
                if _many_call_debug_: print 'many call debug: func %s: result %s'%(f, updates)
            except exceptions.Exception,e:
                raise ManyCallException('call func with exception %s'%traceback.format_exc(), (f,e))
            if type(updates) != dict:
                raise ManyCallException('func %s call not return a dict',
                                        getattr(f, 'func_name', "unknown"), (kw, updates))
            result.update(updates)
        return result

    def __call__(self, **kw):
        return self.call(**kw)
    
    def __lshift__(self, func):
        self.reg(func)

def nil_action(**kw):
    pass

class LazyMan(ManyCall):
    def __init__(self):
        ManyCall.__init__(self)

    def gen_deps(self, static_deps=[], pattern_deps=[], extra_deps=[], **task):
        if static_deps:
            deps = static_deps + extra_deps
        else:
            deps = pattern_deps + extra_deps
        return deps
        
    def need_update(self, type='task', **task):
        if type == 'task': return True
        elif type == 'file':
            return False
        else:
            raise LMException('unknown task type: %s'%type, task)

    def do(self, target='default', **attr):
        task = self.call(target=target, **attr)
        result = dict([(msub(dep, task), self.do(**dict_updated(task, target=dep))) for dep in task.get('deps', [])])
        result.update(task)
        return task.get('action', nil_action)(**result)

    def __call__(self, target='default', **task):
        return self.do(target=target, **task)

def msub_object(obj, env):
    if type(obj) == str: return msub(obj, env)
    elif type(obj) == list or type(obj) == tuple:
        return [msub(i, env) for i in obj]
    else: return obj
    
def make_plan(_target, **_attr):
    def plan(target, **attr):
        d = str2dict(_target, target)
        if not d: return {}
        new_attr = dict([(k, msub_object(v, d)) for k,v in _attr.items()])
        new_attr.update(d)
        return dict(attr, **dict_updated(new_attr, target=target))
    return plan

def echo(**task):
    return pprint.pformat(task)

def make_shell_action(cmd):
    def shell_action(**task):
        expanded_cmd = msub(cmd, task)
        shell(expanded_cmd)
    return shell_action

sh = make_shell_action
mkp = make_plan

if __name__ == '__main__':
    # m = ManyCall()
    # m << (lambda seq: {'sum': 100})
    # m << (lambda seq: {'sum':m.nil_setter(sum(seq))})
    # m << (lambda seq: {'mean':sum(seq)/len(seq)})
    # print m(seq=range(10))
    lm = LazyMan()
    lm << mkp('what do $you want',
              deps=['what_${you}_prefer', 'how_many_${you}_eat'],
              action=sh('echo $you want $how_many_${you}_eat $what_${you}_prefer and $others and $others2'),
              others='other good things')
    lm << mkp('what_book11_prefer', deps=[], action=lambda **kw:'apple')
    lm << mkp('how_many_book11_eat', deps=[], action=lambda **kw:42)
    print lm('what do book11 want', _many_call_debug_=False, others='others', others2='bla bla')
