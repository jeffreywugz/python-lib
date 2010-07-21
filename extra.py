from common import *
from render import *
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

def _make_dir_cmd_views(dir, cmd_views):
    def new_cmd_view(name, cmd, input_visibility=False):
        return name, dir, cmd, input_visibility
    return [new_cmd_view(*i) for i in cmd_views]

def dir_cmd_views(dir, cmd_views, d={}, **kw):
    cmd_views = _make_dir_cmd_views(dir, cmd_views)
    return multi_cmd_views(cmd_views, d, **kw)

def multi_cmd_views(views, d={}, **kw):
    kw = dict_updated(kw, d)
    def make_views(name, dir, cmd, input=False):
        return name, gen_sh_url(dir, sub(cmd, kw), input)
    return [make_views(*v) for v in views]
    
