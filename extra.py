from common import *
import urllib

def gen_list(*ranges):
    def parse(i):
        match = re.match('^([-+])?([0-9]+)(-[0-9]+)?$', i)
        if not match: raise GErr('illformaled range specifier', i)
        type, start, end = match.groups()
        start = int(start)
        if type == None: type = '+'
        if end != None: end = end[1:]
        if end == None or end == '' : end = start + 1
        else: end = int(end)
        return type, range(start, end)
    ranges = [parse(i) for i in ranges]
    included = [r for t, r in ranges if t == '+']
    excluded = [r for t, r in ranges if t == '-']
    included = reduce(lambda x,y: x+y, included, [])
    excluded = reduce(lambda x,y: x+y, excluded, [])
    included = set(included)
    excluded = set(excluded)
    ranges = included - excluded
    return sorted(list(ranges))

class MarkCodec:
    start_tag = '==============================%s=============================='
    end_tag = '------------------------------%s------------------------------'
    def __init__(self, tag='mark'):
        self.tag = tag

    def dumps(self, value):
        return '%s\n%s\n%s' %(self.start_tag % self.tag, repr(value), self.end_tag % self.tag)

    def loads(self, content, default=None):
        match = re.search('%s\n(.*)\n%s'%(self.start_tag % self.tag, self.end_tag % self.tag), content, re.S)
        if not match:
            return default
        expr = match.group(1)
        return eval(expr)
    
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

def ds_run(ds, *cmd, **kw):
    return map(shell, dssub(ds, *cmd, **kw))

def ds_vrun(ds, key, expand_key, *cmd, **kw):
    def target(d, *ds):
        env = dmerge(d, kw)
        return safe_popen(msub(' '.join(cmd), **env))
    return dszip(ds, target, expand_key, key)

def ds_veval(ds, key, expand_key, expr, env, **kw):
    def target(d, *ds):
        sub_env = dmerge(d, kw)
        expand_expr = msub(expr, **sub_env)
        return safe_eval(expand_expr, env)
    return dszip(ds, target, expand_key, key)

class UrlSet:
    def __init__(self, base_url):
        self.base_url = base_url

    def gen(self, url, **kw):
        return '%s/%s?%s'%(self.base_url, url, urllib.urlencode(kw))

core_urls = UrlSet('/ans42/prj/python-lib/bin')

def gen_sh_url(dir, cmd, input=True):
    if input: input_visibility='show'
    else: input_visibility='hidden'
    return core_urls.gen('sh.cgi', workdir=dir, cmd=cmd, input_visibility=input_visibility)

def gen_ed_url(path):
    return core_urls.gen('ed.cgi', path=path)

class Wiki:
    def __init__(self, dir):
        self.dir = dir

    def view(self, path='index.adoc'):
        if not get_ext(path): path = path + '.adoc'
        path = os.path.realpath(os.path.join(self.dir, path))
        views = [('view', gen_sh_url('.', 'asciidoc --out-file=- %s'%path, False)),('edit', gen_ed_url(path))]
        return render_tabs(views)

def multi_cmd_view(views, input=False):
    return [(name, gen_sh_url(dir, cmd, input)) for name, dir, cmd in views]
    
        
