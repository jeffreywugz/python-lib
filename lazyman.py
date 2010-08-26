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

def to_list(x):
    if type(x) == list or type(x) == tuple:
        return x
    else:
        return [x]

def uniq(seq):
    visited = set()
    for i in seq:
        if not i in visited: yield i
        visited.add(i)
        
class ManyCall(object):
    """Similar to Map-Reduce but instead:
      Single-Function(Multiple Data);
    Here:
      Multiple-Functions(Single-Data);
    """
    def __init__(self):
        self.map_funcs, self.reduce_funcs = [], []
        self.debug = False

    def reg_map_func(self, func):
        if not callable(func):
            raise ManyCallException('object is not callable',  func)
        self.map_funcs.append(func)

    def reg_map_funcs(self, funcs):
        for f in to_list(funcs):
            self.reg_map_func(f)
            
    def reg_reduce_func(self, func):
        if not callable(func):
            raise ManyCallException('object is not callable',  func)
        self.reduce_funcs.append(func)

    def reg_reduce_funcs(self, funcs):
        for f in to_list(funcs):
            self.reg_reduce_func(f)
            
    def call_func(self, f, **kw):
        try:
            if self.debug: print 'ManyCall: func %s: args %s'%(f, kw)
            result = f(**kw)
            if self.debug: print 'ManyCall: func %s: result %s'%(f, result)
        except exceptions.Exception,e:
            raise ManyCallException('call func with exception %s'%traceback.format_exc(), (f,e))
        if type(result) != dict:
            raise ManyCallException('func %s not return a dict'%getattr(f, 'func_name', "?"), (kw, result))
        return result
        
    def map_call(self, **kw):
        def result_update(d, u):
            for k,v in u.items():
                li = d.get(k, [])
                if type(li) != list: raise ManyCallException('Internal Error: Got non list value when merge map result')
                li.append(v)
                d[k] = li
            return d
        return reduce(result_update, [self.call_func(f, **kw) for f in self.map_funcs], {})
            
    def reduce_call(self, **kw):
        def dict_merge(dicts):
            return reduce(lambda a,b: a.update(b) or a, dicts, {})
        return dict_merge([self.call_func(f, **kw) for f in self.reduce_funcs])
    
    def call(self, **kw):
        result = self.map_call(**kw)
        result = self.reduce_call(**result)
        return result
    
    def __call__(self, **kw):
        return self.call(**kw)

    def __lshift__(self, f):
        self.reg_map_funcs(f)
        return self

    def __rshift__(self, f):
        self.reg_reduce_funcs(f)
        return self

def keep_last(**kw):
    return dict([(k, v[-1]) for k,v in kw.items()])
    
def keep_uniq(**kw):
    return dict([(k,list(uniq(v))) for k,v in kw.items()])
                  
def nil_action(**kw): return True
def echo(**task): print pprint.pformat(task)

class LazyMan(ManyCall):
    def __init__(self):
        ManyCall.__init__(self)
        self.reg_reduce_func(keep_last)
        self.debug, self.dry_run, self.verbose = False, False, True

    def need_update(self, type='task', **task):
        if type == 'task': return True
        elif type == 'file':
            return False
        else:
            raise LMException('unknown task type: %s'%type, task)

    def do(self, log=BlockStream(), target='default', **attr):
        task = self.call(target=target, **attr)
        if self.verbose: log.out('%s => %s'%(target, task.get('deps', [])))
        deps = task.get('deps', [])
        result = dict([(msub(dep, task), self.do(log=log.new(), **dict_updated(task, target=dep, deps=[], action=nil_action))) for dep in deps])
        result.update(task)
        if self.dry_run: return task
        if task.get('cached', lambda **kw: False)(**result):
            if self.verbose: log.out('%s: cached <<<<<<<<<<'%(target))
            return dict_updated(task, cached=True)
        else:
            result=task.get('action', nil_action)(**result)
            if self.verbose: log.out('%s: complete <<<<<<<<<<'%(target))
            return dict_updated(task, result=result)

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

def make_shell_action(cmd):
    def shell_action(**task):
        env = dict([(k, ' '.join([str(i) for i in to_list(v)]))for k,v in task.items()])
        expanded_cmd = msub(cmd, env)
        print 'shell $ %s'%expanded_cmd
        ret = shell(expanded_cmd)
        if ret: raise LMException("Shell Action Failed with RetCode %d"%(ret), expanded_cmd)
    return shell_action

def file_task_cached(target='', deps=[], **kw):
    if not os.path.exists(target): return False
    mtime = os.path.getmtime(target)
    file_deps = filter(lambda x: x.get('type','') == 'file', [kw.get(d, {}) for d in deps])
    def newer_than_target(file):
        if not os.path.exists(file):
            raise LMException("Dep File not Exist: %s"%file, target)
        return os.path.getmtime(file) > mtime
    return not any([newer_than_target(d['target']) for d in file_deps])

def parse_rule(rule):
    """[<type>] <target>: <deps>[: <{attrs}>]"""
    pat = '(?:(\w+)\s+)?([^:]+)\s*(?::\s*([^{]*))?\s*(?:\s*{([^}]*)})?\s*'
    match = re.match(pat, rule)
    if not match: raise LMException("Ill Formaled Task Specifier", task)
    _type, target, deps, attrs = match.groups()
    print attrs
    _type, deps, attrs = _type or 'file', deps or '', attrs or ''
    deps = deps.split()
    attrs = dict(re.findall('\s*([^=]+)\s*=\s*([^;]*)\s*;', attrs))
    print 'parse_rule: %s/%s => %s | %s'%(_type, target, deps, attrs)
    return _type, target, deps, attrs
    
def simple_make_plan(rule, action, **_attr):
    file_task_attrs = {'type':'file', 'cached':file_task_cached}
    _type, target, deps, attrs = parse_rule(rule)
    if type(action) == str: action = make_shell_action(action)
    if _type == 'file': attrs.update(file_task_attrs)
    attrs.update(_attr)
    return make_plan(target, deps=deps, action=action, **attrs)

def parse_makefile(str):
    pat = '^(\S.+)\n((?:\s+.*\n)*)'
    rules = re.findall(pat, str, re.M)
    return [simple_make_plan(rule, cmds) for rule,cmds in rules]

_mkp = make_plan
mkp = simple_make_plan
sh = make_shell_action

if __name__ == '__main__':
    # m = ManyCall()
    # m << (lambda seq,**kw: {'sum': 100})
    # m << (lambda seq,**kw: {'mean':sum(seq)/len(seq)})
    # m >> (lambda mean,**kw: {'result': mean})
    # print m(seq=range(10))
    lm = LazyMan()
    # lm << mkp('$base\.o:$base.c', '$cc -c $cflags -o $target $deps')
    # lm << mkp('$base\.c', 'tpl c > $target')
    # lm << mkp('foo:foo.o', '$cc $ldflags -o $target $deps')
    # lm << mkp('task run:foo', './$deps')
    # lm << mkp('task clean', 'rm -rf *.o')
    rules = '''
$base\.c:
    tpl c > $target
foo.o: foo.c {}
    $cc -c $cflags -o $target $deps
foo:foo.o
    $cc -o $target $deps
task run: foo
    ./$deps
task clean:
    rm -rf foo.o foo.c foo
'''
    lm << parse_makefile(rules)
    lm.dry_run = False
    lm('clean', cc='gcc')
