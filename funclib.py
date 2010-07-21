from functools import *
import itertools
import copy
import re
import itertools
import pprint

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
        return itertools.imap(lambda x:func(x, *args, **kw), stream)
    return wrapper

def flip(func):
    def flip_func(*arg):
        return func(*reversed(*arg))
    return flip_func

def list_flatten(li):
    if type(li) == list or type(li) == tuple:
        return reduce(lambda x,y:x+y, map(lflatten, li), [])
    else:
        return [li]

def step_in(i, steps):
    tail = filter(lambda x: x > i, steps)
    if not tail: return None
    return tail[0]
    
def list_sum(lists):
    result = []
    for list in lists:
        result.extend(list)
    return result

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
    
def dict_make(keys, values):
    return dict(map(None, keys, values))

def dict_merge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dict_match(d, **pat):
    return set(pat.items()) <= set(d.items())

def dict_slice(d, *keys):
    return map(lambda x: d[x], keys)

def dict_updated(d, extra={}, **kw):
    new_dict = copy.copy(d)
    new_dict.update(extra, **kw)
    return new_dict

def dict_updated_by_callables(d, **kw):
    new_dict = copy.copy(d)
    new_dict.update([(k,v(**d)) for k,v in kw.items()])
    return new_dict
                  
def dict_map(func, d):
    return dict([(k, func(v)) for (k,v) in d.items()])

def dc_mul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dc_map(func, *args):
    list = dc_mul(*args)
    return map(lambda x:func(*x), list)

