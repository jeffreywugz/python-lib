from functools import *

def compose(func_1, func_2):
    def composition(*args, **kwargs):
        return func_1(func_2(*args, **kwargs))
    return composition

def unpack(func):
    def unpack_func(args):
        if type(args) == dict:
            return func(**args)
        elif type(args) == list or type(args) == tuple:
            return func(*args)
        else:
            return func(args)
    return unpack_func

def flip(func):
    def flip_func(*arg):
        return func(*reversed(*arg))
    return flip_func

def lflatten(li):
    if type(li) == list or type(li) == tuple:
        return reduce(lambda x,y:x+y, map(lflatten, li), [])
    else:
        return [li]
    
def dmerge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dmatch(d, **pat):
    return set(pat.items()) <= set(d.items())

def dmap(func, d):
    return dict([(k, func(v)) for (k,v) in d.items()])

def dcmul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dcmap(func, *args):
    list = dcmul(*args)
    return map(lambda x:func(*x), list)
    
def msub(template, **env):
    old = ""
    cur = template
    while cur != old:
        old = cur
        cur = sub(cur, **env)
    return cur

class DictSet:
    def __init__(self, *args, **kw):
        def to_list(v):
            if type(v) == list or type(v) == tuple: return v
            else: return [v]
        def to_dicts(k, vs):
            return [{k: v} for v in vs]
        single_key_dicts = [to_dicts(k, to_list(v)) for (k,v) in kw.items()]
        dicts = args + tuple(single_key_dicts)
        self.dicts = dcmap(dmerge, *dicts)

    def query(self, **kw):
        return filter(lambda x: dmatch(x, **kw), self.dicts)

    def update(self, **kw):
        map(lambda env: env.update(dmap(lambda v: v(**env), kw)), self.dicts)

    def map(self, func):
        return dmap(func, self.dicts)
    
    def __mul__(self, dicts):
        return DictSet(self.dicts, dicts)
    
