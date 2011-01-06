from functools import *
import itertools
import copy
import re
import itertools
import pprint
from core import *

######################################## Func ########################################
def counter(d, x):
    if not d.has_key(x): d[x] = 0
    d[x] += 1
    return d[x]
    
def identity(x):
    return x

def _compose(func1, func2):
    def composition(*args, **kwargs):
        return func1(func2(*args, **kwargs))
    return composition

def compose(*funcs):
    return reduce(_compose, funcs, identity)

def unpack(func):
    def unpack_func(args):
        if type(args) == dict:
            return func(**args)
        elif type(args) == list or type(args) == tuple:
            return func(*args)
        else:
            return func(args)
    return unpack_func

def make_filter(func):
    def wrapper(stream, *args, **kw):
        return map(lambda x:func(x, *args, **kw), stream)
    return wrapper

def flip(func):
    def flip_func(*arg):
        return func(*reversed(*arg))
    return flip_func

######################################## List ########################################
def list_flatten(li):
    if type(li) == list or type(li) == tuple:
        return reduce(lambda x,y:x+y, list(map(list_flatten, li)), [])
    else:
        return [li]

def step_in(i, steps):
    tail = [x for x in steps if x > i]
    if not tail: return None
    return tail[0]

def uniq(seq):
    d = {}
    return filter(lambda x: counter(d, x) == 1, seq)
           
# def list_sum(lists):
#     result = []
#     for list in lists:
#         result.extend(list)
#     return result

def list_merge(*l):
    return reduce(lambda a,b: list(a)+list(b), l, [])

def list_split(l, *sep):
    result = [[]]
    for i in l:
        if i in sep:
            result.append([])
        else:
            result[-1].append(i)
    return result

######################################## Dict ########################################
def dict_make(keys, values):
    return dict(map(None, keys, values))

def dict_merge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dict_match(d, **pat):
    return all([d.get(k) == v for k,v in pat.items()])

def dict_rematch(d, **pat):
    return all([re.match(v, d.get(k, '')) for(k,v) in pat.items()])
    
def dict_slice(d, *keys):
    return [d.get(x) for x in keys]

def dict_slice2(d, *keys):
    return dict([(x, d.get(x)) for x in keys])

def dict_map(func, d):
    return dict([(k, func(v)) for (k,v) in list(d.items())])

def dict_trans(d, **kw):
    def call_or_not(v, d):
        if callable(v): return v(**d)
        else: return d
    return dict_map(lambda v: call_or_not(v, d), kw)
    
def dict_updated(d, extra={}, **kw):
    new_dict = copy.copy(d)
    new_dict.update(extra, **kw)
    return new_dict

def dict_updated_ex(d, extra={}, **kw):
    new_dict = dict_trans(d, **dict_updated(extra, kw))
    new_dict = dict_updated(d, new_dict)
    return dict_updated(new_dict, new_dict.get('_inline_') or {})

def dc_mul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dc_map(func, *args):
    list = dc_mul(*args)
    return [func(*x) for x in list]

######################################## String ########################################
def joiner(sep=' '):
    return lambda seq: sep.join(map(str,seq))

def sub2(_str, env=globals(), **kw):
    """Example: $abc ${abc} ${range(3)|> joiner()}"""
    def pipe_eval(ps, env):
        return reduce(lambda x,y: y(x), [safe_eval(p, env) for p in ps.split('|>')])
    return re.sub('(?s)\$(\w+)|\$(?:{(.+?)})', lambda m: str(pipe_eval(m.group(2) or m.group(3), dict_updated(env, kw))), _str)
    
def sub(template, env={}, **vars):
    return string.Template(template).safe_substitute(env, **vars)

def msub(template, env={}, **kw):
    old = ""
    cur = template
    new_env = copy.copy(env)
    new_env.update(kw)
    while cur != old:
        old = cur
        cur = sub(cur, new_env)
    return cur

def str2dict(template, str):
    def normalize(str):
        return re.sub('\$(\w+)', r'${\1:\w+}', str)
    def tore(str):
        return re.sub(r'\${(\w+):([^}]+)}', r'(?P<\1>\2)', str)
    rexp = '^%s$' % (tore(normalize(template)))
    match = re.match(rexp, str)
    if not match: return {}
    else: return dict(match.groupdict(), __self__=str)

def tpl_sub(tpl, target, str):
    env = str2dict(tpl, str)
    env.update(_=str)
    return sub(target, env)

def tpl_shell(tpl, cmd, str):
    cmd = tpl_sub(tpl, cmd, str)
    print(cmd)
    shell(cmd)
    

