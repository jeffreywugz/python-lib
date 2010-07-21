from common import *

def render_list_as_html(ds, *cols):
    return core_templates.render('list.html', data=ds, cols=cols)
    
def render_list_as_txt(ds, *cols):
    def safe_dslice(d, *keys):
        return map(lambda x: d.get(x, None), keys)
    data = [safe_dslice(d, *cols) for d in ds]
    data = [cols] + data
    data = map(lflatten, data)
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

def render_ds(ds, head, terminal='html', sortkey=None):
    render = globals().get('render_list_as_%s'%(terminal), None)
    if not render:
        return "No terminal defined for %s" % terminal
    cols = sorted(ds_keys(ds), key=sortkey)
    cols.remove(head)
    cols.insert(0, head)
    return render(ds, *cols)
