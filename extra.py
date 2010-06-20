from common import *
import urllib

def render_list(ds, *cols):
    return core_templates.render('list.html', data=ds, cols=cols)
    
def render_table(cell_maker, rows, cols):
    return core_templates.render('table.html', cell_maker=cell_maker, rows=rows, cols=cols)

def render_ds(ds, head, sortkey=None):
    cols = sorted(dskeys(ds), key=sortkey)
    cols.remove(head)
    cols.insert(0, head)
    return render_list(ds, *cols)

# class MultiShell(VisualDictSet):
#     def __init__(self, *args, **kw):
#         VisualDictSet.__init__(self, *args, **kw)

#     def sub(self, *cmd, **kw):
#         dicts = self * kw
#         return dicts.map(lambda **env: msub(' '.join(cmd), **env))

#     def run(self, *cmd, **kw):
#         return map(shell, self.sub(*cmd, **kw))

#     def vrun(self, row, col, *cmd, **kw):
#         def cell_maker(**env):
#             env = dmerge(env, kw)
#             return safe_popen(msub(' '.join(cmd), **env))
#         return self.table_view(target=cell_maker, row=row, col=col)

#     def filter(self, **kw):
#         return type(self)(self.query(**kw))

#     def qrun(self, *cmd, **kw):
#         return self.filter(**kw).run(*cmd)

#     def qvrun(self, row, col, *cmd, **kw):
#         return self.filter(**kw).vrun(row, col, *cmd)
    
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

