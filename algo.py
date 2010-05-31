def flatten_list(li):
    if type(li) == list or type(li) == tuple:
        return reduce(lambda x,y:x+y, map(flatten_list, li), [])
    else:
        return [li]
    
def mget(mlist, **args):
    def match(item):
        for key, value in args.items():
            if not item.has_key(key):
                return False
            if item[key] != value:
                return False
        return True
    return filter(match, mlist)

def dcmul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dcmap(func, *args):
    list = dcmul(*args)
    return map(lambda x:func(*x), list)
    
def dmerge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dmap(func, *dicts):
    list = dcmap(dmerge, *dicts)
    return map(func, list)
    
def lset(list, name, func):
    return [i.update(**{name:func(i)}) for i in list]

def lquery(list, **kw):
    def match(item, kw):
        return set(kw.items()) <= set(item.items())
    return filter(lambda x: match(x, kw), list)
