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

def mkfilter(func):
    def wrapper(stream, *args, **kw):
        return itertools.imap(lambda x:func(x, *args, **kw), stream)
    return wrapper

def flip(func):
    def flip_func(*arg):
        return func(*reversed(*arg))
    return flip_func

def lflatten(li):
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

def lmerge(*l):
    return reduce(lambda a,b: list(a)+list(b), l, [])

def lsplit(l, *sep):
    result = [[]]
    for i in l:
        if i in sep:
            result.append([])
        else:
            result[-1].append(i)
    return result
    
def mkdict(keys, values):
    return dict(map(None, keys, values))

def mkds(keys, values_list):
    return [mkdict(keys, values) for values in values_list]

def dmerge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dmatch(d, **pat):
    return set(pat.items()) <= set(d.items())

def dslice(d, *keys):
    return map(lambda x: d[x], keys)

def dupdated(d, **kw):
    new_dict = copy.copy(d)
    new_dict.update([(k,v(**d)) for k,v in kw.items()])
    return new_dict
                  
def dmap(func, d):
    return dict([(k, func(v)) for (k,v) in d.items()])

def dcmul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dcmap(func, *args):
    list = dcmul(*args)
    return map(lambda x:func(*x), list)

def dsgroup(ds, *keys):
    def keyfunc(d):
        return dslice(d, *keys)
    return itertools.groupby(sorted(ds, key=keyfunc), keyfunc)

def dscollpse(ds, target, key):
    return dict([(k[0], target(*v)) for k,v in dsgroup(ds, key)])

def dszip(ds, target, expand_key, *key):
    return [dmerge(mkdict(key, k), dscollpse(v, target, expand_key)) for k,v in dsgroup(ds, *key)]

def dskeys(ds):
    keys = lmerge(*map(lambda d:d.keys(), ds))
    return list(set(keys))

def dsfilter(ds, **kw):
    return filter(lambda d:dmatch(d, **kw), ds)

