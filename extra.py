from common import *
import urllib

class VisualDictSet(DictSet):
    def __init__(self, *args, **kw):
        DictSet.__init__(self, *args, **kw)

    def enum_attr_values(self, attr):
        attr_values = self.map(lambda **d: d.get(attr, None))
        attr_values = filter(lambda x: x != None, attr_values)
        return sorted(list(set(attr_values)))
        
    def list_view(self, *cols):
        return core_templates.render('list.html', data=self.dicts, cols=cols)

    def make_cell_maker(self, row, col, func, multiple=False):
        def cell_maker(row_value, col_value):
            result = self.query(**{col: col_value, row: row_value})
            if multiple:
                return func(*result)
            else:
                if len(result) == 0: return None
                else: return func(**result[0])
        return cell_maker
        
    def table_view(self, target, row, col):
        def default_cell_maker(**kw):
            return kw[target]
        
        if callable(target): cell_maker = self.make_cell_maker(row, col, target)
        else: cell_maker = self.make_cell_maker(row, col, default_cell_maker)
        
        rows = self.enum_attr_values(row)
        cols = self.enum_attr_values(col)
        return core_templates.render('table.html', cell_maker=cell_maker, rows=rows, cols=cols)
        

class MultiShell(VisualDictSet):
    def __init__(self, *args, **kw):
        VisualDictSet.__init__(self, *args, **kw)

    def sub(self, *cmd, **kw):
        dicts = self * kw
        return dicts.map(lambda **env: msub(' '.join(cmd), **env))

    def run(self, *cmd, **kw):
        return map(shell, self.sub(*cmd, **kw))

    def vrun(self, row, col, *cmd, **kw):
        def cell_maker(**env):
            env = dmerge(env, kw)
            return safe_popen(msub(' '.join(cmd), **env))
        return self.table_view(target=cell_maker, row=row, col=col)

    def filter(self, **kw):
        return MultiShell(self.query(**kw))

class UrlSet:
    def __init__(self, base_url):
        self.base_url = base_url

    def gen_url(self, url, **kw):
        return '%s/%s?%s'%(self.base_url, url, urllib.urlencode(kw))

core_urls = UrlSet('/ans42/prj/python-lib/bin')

class Wiki:
    def __init__(self, dir):
        self.dir = dir

    def view(self, path):
        path = os.path.realpath(os.path.join(self.dir, path))
        views = [('view', core_urls.gen_url('sh.cgi', input_visibility='hidden', cmd='asciidoc --out-file=- %s'%path)),('edit', core_urls.gen_url('ed.cgi', path=path))]
        return core_templates.render('tabs.html', views=views)

