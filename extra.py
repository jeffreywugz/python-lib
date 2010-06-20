from common import *
import urllib

def render_list_as_html(ds, *cols):
    return core_templates.render('list.html', data=ds, cols=cols)
    
def render_list_as_txt(ds, *cols):
    data = [dslice(d, *cols) for d in ds]
    data = [cols] + data
    def list2str(items):
        return ',\t'.join([str(x).strip() for x in items])
    return '\n'.join([list2str(items) for items in data])

def render_table(cell_maker, rows, cols):
    return core_templates.render('table.html', cell_maker=cell_maker, rows=rows, cols=cols)

def render_ds(ds, head, terminal='html', sortkey=None):
    render = globals().get('render_list_as_%s'%(terminal), None)
    if not render:
        return "No terminal defined for %s" % terminal
    cols = sorted(dskeys(ds), key=sortkey)
    cols.remove(head)
    cols.insert(0, head)
    return render(ds, *cols)

def dssub(ds, *tpl, **kw):
    ds = dcmap(dmerge, ds, [kw])
    return map(lambda env: msub(' '.join(tpl), **env), ds)

def msh_run(ds, *cmd, **kw):
    return map(shell, dssub(ds, *cmd, **kw))

def msh_vrun(ds, key, expand_key, *cmd, **kw):
    def target(d, *ds):
        env = dmerge(d, kw)
        return safe_popen(msub(' '.join(cmd), **env))
    return dszip(ds, target, expand_key, key)
    
class UrlSet:
    def __init__(self, base_url):
        self.base_url = base_url

    def gen_url(self, url, **kw):
        return '%s/%s?%s'%(self.base_url, url, urllib.urlencode(kw))

core_urls = UrlSet('/ans42/prj/python-lib/bin')

class Wiki:
    def __init__(self, dir):
        self.dir = dir

    def view(self, path='index.adoc'):
        path = os.path.realpath(os.path.join(self.dir, path))
        views = [('view', core_urls.gen_url('sh.cgi', input_visibility='hidden', cmd='asciidoc --out-file=- %s'%path)),('edit', core_urls.gen_url('ed.cgi', path=path))]
        return core_templates.render('tabs.html', views=views)

