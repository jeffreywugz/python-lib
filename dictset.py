from common import *

def ds_make(keys, values_list):
    return [dict_make(keys, values) for values in values_list]

def ds_group(ds, *keys):
    def keyfunc(d):
        return dict_slice(d, *keys)
    return itertools.groupby(sorted(ds, key=keyfunc), keyfunc)

def ds_collapse(ds, target, key):
    return dict([(k[0], target(*v)) for k,v in ds_group(ds, key)])

def ds_zip(ds, target, expand_key, *key):
    return [dict_merge(dict_make(key, k), ds_collapse(v, target, expand_key)) for k,v in ds_group(ds, *key)]

def ds_keys(ds):
    keys = list_merge(*map(lambda d:d.keys(), ds))
    return list(set(keys))

def ds_filter(ds, **kw):
    return filter(lambda d:dict_match(d, **kw), ds)

def ds_updated(ds, d={}, **kw):
    new_dict = dict_updated(d, kw)
    return [dict_updated(d, new_dict) for d in ds]

def ds_filter_by_key(ds, key, *values):
    filter(lambda d: d[key] in values, ds)

def ds_updated_by_sub(ds, d={}, **kw):
    kw = dict_updated(d, kw)
    def sub_updated(d, kw):
        new_kw = dict_map(lambda v: msub(v, dict_updated(d, **kw)), kw)
        return dict_updated(d, new_kw)
    return [sub_updated(d, kw) for d in ds]
                     
def ds_updated_by_eval(ds, globals, locals={}, d={}, **kw):
    kw = dict_updated(d, kw)
    def eval_updated(d, kw):
        new_kw = dict_map(lambda v: msub(v, dict_updated(d, **kw)), kw)
        new_kw = dict_map(lambda v: eval(v, globals, locals), new_kw)
        return dict_updated(d, new_kw)
    return [eval_updated(d, kw) for d in ds]

def ds_updated_by_popen(ds, d={}, **kw):
    kw = dict_updated(d, kw)
    def popen_updated(d, kw):
        new_kw = dict_map(lambda v: msub(v, dict_updated(d, **kw)), kw)
        new_kw = dict_map(lambda v: safe_popen(v), new_kw)
        return dict_updated(d, new_kw)
    return [popen_updated(d, kw) for d in ds]
                
def ds_zip_sub(ds, key, expand_key, tpl, **kw):
    def target(d, *ds):
        env = dict_merge(d, kw)
        return msub(tpl, **env)
    return ds_zip(ds, target, expand_key, key)
    
def ds_zip_eval(ds, key, expand_key, expr, env, **kw):
    def target(d, *ds):
        sub_env = dict_merge(d, kw)
        expand_expr = msub(expr, **sub_env)
        return safe_eval(expand_expr, env)
    return ds_zip(ds, target, expand_key, key)

def ds_zip_popen(ds, key, expand_key, *cmd, **kw):
    def target(d, *ds):
        env = dict_merge(d, kw)
        return safe_popen(msub(' '.join(cmd), **env))
    return ds_zip(ds, target, expand_key, key)

