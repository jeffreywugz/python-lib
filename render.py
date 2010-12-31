from common import *
from mako.template import Template

def xsub(pat, sep=' ', **env):
    pat = re.sub('\$(\w+)', '${\\1}', pat)
    segments = re.split('(?s)(\${.+?})', pat)
    def evil(seg):
        if not re.match('\$', seg): return seg
        exp = re.sub('(?s)^\${(.+?)}', '\\1', seg)
        result = eval(exp, globals(), env)
        if type(result) != list and type(result) != tuple:
            result = [result]
        return sep.join([str(item) for item in result])
    return ''.join([evil(seg) for seg in segments])

class TemplateSet:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        
    def render(self, file, **kw):
        return Template(filename=os.path.join(self.base_dir, file)).render(**kw)
        
core_templates = TemplateSet(os.path.join(my_lib_dir, 'res'))

def render_list_as_html2(ds, *cols):
    tpl = """<div><table border="1" width="100%">
  <tr style="background: black; color: white; font-weight: bold;">${['<td>%s</td>'%col for col in cols]}</tr>
  ${['<tr>%s</tr>'% ' '.join(['<td><pre>%s</pre></td>'% item.get(col, None) for col in cols]) for item in data]}
  </table></div>"""
    return xsub(tpl, data=ds, cols=cols)

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
        return '\t'.join([toStr(x).strip() for x in items])
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
    _rest = tuple(sorted(set(ds_keys(ds)) - set(cols[:-1])))
    if cols[-1] == '__rest__':
        cols = cols[:-1] + _rest
    elif cols[-1] == '_rest_':
        cols = cols[:-1] + filter(lambda x: not x.startswith('_'), _rest)
    render = globals().get('render_list_as_%s'%(term), None)
    if not render:
        return "No terminal defined for %s" % term
    return render(ds, *cols)

def plot_list(ds, term, *cols):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    def plt_dump(term):
        if term.endswith('.show'): plt.show()
        elif term.endswith('.html'):
            img = '/local/%s'%term.replace('.html', '.png')
            plt.savefig(img)
            return '<img src="%s" alt="img not found!"/>'% img
        else: plt.savefig(term)
    
    if not cols or not ds: return
    x, ys = cols[0], cols[1:]
    if not ys: x, ys = '_auto_', [x]
    _x = ds_get(ds, x)
    if type(_x[0]) == float or type(_x[0]) == int:
        xticks = None
    else:
        xticks, _x = _x, range(len(_x))
    if xticks:
        w = 0.8/len(ys)
        colors = 'bgrcmy'
        for i,y in enumerate(ys): plt.bar(np.array(_x)+i*w, ds_get(ds, y), w, label=y, color=colors[i%len(colors)])
        plt.xticks(_x, xticks)
    else:
        for y in ys: plt.plot(_x, ds_get(ds, y), label=y)
    plt.title(re.sub('\..*?$', '', term))
    plt.xlabel(x)
    plt.legend()
    return plt_dump(term)
        
