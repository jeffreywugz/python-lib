from common import *

def render_list_as_html(ds, *cols):
    return core_templates.render('list.html', data=ds, cols=cols)
    
def render_list_as_txt(ds, *cols):
    def safe_dslice(d, *keys):
        return [d.get(x, None) for x in keys]
    data = [safe_dslice(d, *cols) for d in ds]
    data = [cols] + data
    def toStr(x):
        if type(x) == list or type(x) == tuple:
            return '-'.join([str(i) for i in x])
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
    if not cols: return None
    if cols[-1] == '_rest_':
        cols = cols[:-1] + tuple(sorted(set(ds_keys(ds)) - set(cols[:-1])))
    render = globals().get('render_list_as_%s'%(term), None)
    if not render:
        return "No terminal defined for %s" % term
    return render(ds, *cols)
