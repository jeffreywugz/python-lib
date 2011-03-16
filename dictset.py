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

def ds_filter1(ds, **kw):
    return (ds_filter(ds, **kw) or [{}])[0]

def ds_refilter(ds, **kw):
    return [d for d in ds if dict_rematch(d, **kw)]

def ds_slice(ds, *keys):
    return [dict_make(keys, dict_slice(d, *keys)) for d in ds]

def ds_filter_by_key(ds, key, *values):
    [d for d in ds if d[key] in values]
    
def ds_updated(ds, **kw):
    return [dict_updated(d, kw) for d in ds]

def ds_updated_ex(ds, **kw):
    return [dict_updated_ex(d, kw) for d in ds]

def ds_merge(ds, ds2, *keys):
    return [dict_updated(d, ds_filter1(ds2, **dict_slice2(d, *keys))) for d in ds]

def ds_group(ds, *keys):
    return itertools.groupby(sorted(ds, key=lambda d: dict_slice(d, *keys)), lambda d: dict_slice(d, *keys))

def ds2dict(ds, keys, target):
    return dict([(':'.join(k), target(*v)) for k,v in ds_group(ds, *keys)])

def ds_zip(ds, keys, attrs_generator=const({})):
    return [dict_merge(dict_make(keys, k), attrs_generator(*v)) for k,v in ds_group(ds, *keys)]

def ds2table(ds, cols, headers, cell_generator, row_attrs=const({})):
    origin = ds_zip(ds, cols, lambda *part_ds: ds2dict(part_ds, headers, cell_generator))
    row_extra = ds_zip(ds, cols, row_attrs)
    return ds_merge(origin, row_extra, *cols)

def ds_aggregation(ds, aggs):
    aggs = [(k,v(ds)) for k,v in aggs]
    return ds + aggs

def ds_matv(ds, features, aggs):
    ds = ds_updated_ex(ds, **dict(features))
    ds = ds_aggregation(ds, aggs)
    return ds
