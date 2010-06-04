from functools import *

# def compose(func_1, func_2):
#     def composition(*args, **kwargs):
#         return func_1(func_2(*args, **kwargs))
#     return composition

# def unpack(func):
#     def unpack_func(args):
#         if type(args) == dict:
#             rerutn func(**args)
#         elif type(args) == list || type(args) == tuple:
#             return func(*args)
#         else:
#             return func(args)
#     return unpack_func

# def flip(func):
#     def flip_func(*arg):
#         return func(*reversed(*arg))
#     return flip_func

def lflatten(li):
    if type(li) == list or type(li) == tuple:
        return reduce(lambda x,y:x+y, map(lflatten, li), [])
    else:
        return [li]
    
def dmerge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dmatch(pat, d):
    return set(pat.items()) <= set(d.items())

def dcmul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dcmap(func, *args):
    list = dcmul(*args)
    return map(lambda x:func(*x), list)
    
def lset(list, name, func):
    return [i.update(**{name:func(**i)}) for i in list]

def lquery(list, **kw):
    return filter(lambda x: match(x, kw), list)

def msub(template, **env):
    old = ""
    cur = template
    while cur != old:
        old = cur
        cur = sub(cur, **env)
    return cur
