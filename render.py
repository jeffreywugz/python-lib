from common import *

def render_list_as_html(ds, *cols, **kw):
    tpl = """<div><table border="1" width="100%">
  <tr style="background: black; color: white; font-weight: bold;">${li('<td>%s</td>')(cols)}</tr>
  ${li('<tr>%s</tr>')([li('<td><pre>%s</pre></td>')([item.get(col, None) for col in cols]) for item in data])}
  </table></div>"""
    return sub2(tpl, data=ds, cols=cols)

def render_list_as_txt(ds, *cols, **kw):
    def safe_dslice(d, *keys):
        return [d.get(x, None) for x in keys]
    data = [safe_dslice(d, *cols) for d in ds]
    data = [cols] + data
    def list2str(items):
        return '\t'.join([str(x) for x in items])
    return '\n'.join([list2str(items) for items in data])

def ds_keys(ds):
    keys = list_merge(*[list(d.keys()) for d in ds])
    return list(set(keys))

def render_list(ds, term, *cols, **kw):
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

def plot_list_as_img(ds, *cols, **kw):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    file = kw.get('file', 'a.png')
    def plt_dump(file):
        if file.endswith('.show'): plt.show()
        else: plt.savefig(file)
    
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
    plt.title(re.sub('\..*?$', '', file))
    plt.xlabel(x)
    plt.legend()
    return plt_dump(file)
        
