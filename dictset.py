from common import *

def ds_make(keys, values_list):
    return [dict_make(keys, values) for values in values_list]

def ds_keys(ds):
    keys = list_merge(*[list(d.keys()) for d in ds])
    return list(set(keys))

def ds_get(ds, key):
    if key == '_auto_': return range(len(ds))
    return [d.get(key) for d in ds]
    
def ds_mget(ds, *keys):
    return [dict_slice(d, *keys) for d in ds]

def ds_filter(ds, **kw):
    return [d for d in ds if dict_match(d, **kw)]

def ds_refilter(ds, **kw):
    return [d for d in ds if dict_rematch(d, **kw)]

def ds_slice(ds, *keys):
    return [dict_make(keys, dict_slice(d, *keys)) for d in ds]

def ds_filter_by_key(ds, key, *values):
    [d for d in ds if d[key] in values]
    
def ds_updated(ds, **kw):
    return [dict_updated(d, kw) for d in ds]

def ds_group(ds, *keys):
    return itertools.groupby(sorted(ds, key=lambda d: dict_slice(d, *keys)), lambda d: dict_slice(d, *keys))

def ds_collapse(ds, keys, target):
    return dict([(':'.join(k), target(*v)) for k,v in ds_group(ds, *keys)])

def _ds_zip(ds, keys, target):
    return [dict_merge(dict_make(keys, k), target(v)) for k,v in ds_group(ds, *keys)]

def ds_zip(ds, zip_keys, expanded_keys, target):
    return _ds_zip(ds, zip_keys, lambda part_ds: ds_collapse(part_ds, expanded_keys, target))

