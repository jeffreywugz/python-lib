'''
data structure, algorithm
'''
from functools import *
import itertools
import copy

class CheckException(Exception):
    def __init__(self, msg, obj=None):
        Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "CheckTypeOnObj: %s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'CheckException(%s, %s)'%(repr(self.msg), repr(self.obj))

def safe_eval(expr, globals={}, locals={}, default=None):
    try:
        return eval(expr, globals, locals)
    except Exception as e:
        return default
    
class Env(dict):
    def __init__(self, d={}, **kw):
        dict.__init__(self)
        self.update(d, **kw)

    def __getattr__(self, name):
        return self.get(name)

######################################## Func ########################################
def ck(predict, obj, msg):
    if not predict:
        raise CheckException(obj, msg)

def ckt(obj, _type):
    def is_seq(obj): type(obj) in [list, tuple]
    def is_map(obj): type(obj) in [dict]
    def is_str(obj): type(obj) in [str]
    def is_int(obj): type(obj) in [int]
    def is_func(obj): callable(obj)
    if type(_type) != str: raise CheckException(_type, "cktype(): argument `type' is not str")
    checker =locals().get('is_%s'%_type)
    if not checker: raise CheckException(_type, "cktype(): argument `type' is not defined")
    ck(checker(obj), obj, 'Require Type: %s'%_type)

def counter(d, x):
    if not d.has_key(x): d[x] = 0
    d[x] += 1
    return d[x]
    
def identity(x):
    return x

def const(v):
    return lambda *args, **kw: v

def first(i, *seq):
    return i

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
def list_get(li, idx, default=None):
    if len(li) > idx: return li[idx]
    else: return default
    
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

def transpose(matrix):
    cols = [[] for i in matrix[0]] # Note: You can not write cols = [[]] * len(matrix[0]); if so, all col in cols will ref to same list object 
    for row in matrix:
        map(lambda col,i: col.append(i), cols, row)
    return cols

