from common import *

def render_list_as_html(ds, *cols):
    return core_templates.render('list.html', data=ds, cols=cols)
    
def render_list_as_txt(ds, *cols):
    def safe_dslice(d, *keys):
        return map(lambda x: d.get(x, None), keys)
    data = [safe_dslice(d, *cols) for d in ds]
    data = [cols] + data
    data = map(list_flatten, data)
    def toStr(x):
        x = str(x)
        if x.startswith('Error:'): return 'Error'
        else: return x
    def list2str(items):
        return ',\t'.join([toStr(x).strip() for x in items])
    return '\n'.join([list2str(items) for items in data])

def render_table(cell_maker, rows, cols):
    return core_templates.render('table.html', cell_maker=cell_maker, rows=rows, cols=cols)

def render_panels(views):
    return core_templates.render('panels.html',views=views)

def render_tabs(views):
    return core_templates.render('tabs.html', views=views)
    
def render_obj(obj, exported=None):
    if exported == None: exported = obj.exported
    views = [(attr, getattr(obj, attr)) for attr in exported]
    return render_tabs(views)

def render_list(ds, term, *cols):
    render = globals().get('render_list_as_%s'%(term), None)
    if not render:
        return "No terminal defined for %s" % term
    return render(ds, *cols)

def render_ds_simple(ds, key, term='html'):
    def keys_sorted(first, keys, key=None):
        keys.remove(first)
        keys = sorted(keys, key=key)
        return [first] + keys
    return render_list(ds, term, *keys_sorted(key, ds_keys(ds)))
    
def render_ds(ds, term='html'):
    if not ds: return ''
    cols_to_zip = ds[0].get('_cols_to_zip_') 
    if cols_to_zip:
        key, expanded, tpl = cols_to_zip
        ds = ds_zip_sub(ds, key, expanded, tpl)
        return render_ds_simple(ds, key, term)
    cols_to_render = ds[0].get('_cols_to_render_')
    return render_list(ds, term, *cols_to_render)
