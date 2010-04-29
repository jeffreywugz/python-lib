import os
import sys
import operator
import re
from glob import glob

class BlockStream:
    tab_stop = '    '
    Debug, Info, Warning, Error = 1, 0, -1, -2
    threshold = Info
    def __init__(self, stream=sys.stdout, level=Info, indent=0):
        self.stream, self.level, self.indent = stream, level, indent

    def new(self, level=None):
        if level==None: level = self.level
        return BlockStream(self.stream, level, self.indent+1)

    def out(self, content):
        if self.level > self.threshold:return
        self.stream.writelines(["%s%s\n"%(self._get_indent(), line) for line in content.split('\n')])

    def _get_indent(self):
        return self.tab_stop * self.indent

    def __lshift__(self, content):
        self.out(content)

def list_(li):
    if type(li) == list or type(li) == tuple:
        return reduce(operator.add, map(list_, li), [])
    else:
        return [li]
    
def files(*arg):
    return list_([glob(item) for item in list_(arg)])

def ext(filelist_, suffix):
    def _ext(file_name, suffix):
        return re.sub('\.\w+$', '.%s'%suffix, file_name)
    return [_ext(file, suffix) for file in list_(filelist_)]

def update_file(name, content):
    def need_update(name, content):
        if not os.path.exists(name):
            return True
        return open(name).read() != content
    if need_update(name, content):
        file = open(name, 'w')
        file.write(content)
        file.close()
        return True
    return False

def lower_case(str):
    return '_'.join(filter(None, re.split('([A-Z][a-z]+)',  str))).lower()

class Env(dict):
    def __init__(self, d={}, **kw):
        dict.__init__(self)
        self.update(d, **kw)

    def __getattr__(self, name):
        return self.get(name)

def mget(mlist, **args):
    def match(item):
        for key, value in args.items():
            if not item.has_key(key):
                return False
            if item[key] != value:
                return False
        return True
    return filter(match, mlist)

class Templet:
    def __init__(self, str):
        self.str = str

    def sub(self, sep=' ', env={}, **kw):
        preprocessed = re.sub('\$(\w+)', '${\\1}', self.str)
        segments = re.split('(?s)(\${.+?})', preprocessed)
        env.update(**kw)
        def evil(seg):
            if not re.match('\$', seg):
                return seg
            exp = re.sub('(?s)^\${(.+?)}', '\\1', seg)
            result = eval(exp, globals(), env)
            return sep.join([str(item) for item in list_(result)])
        return ''.join([evil(seg) for seg in segments])

def sub(template, env={}, sep=' ', **kw):
    return Templet(template).sub(env=env, sep=sep, **kw)

class TagNotMatch(Exception):
    def __init__(self, begin, end):
        self.begin, self.end = begin, end

    def __str__(self):
        return 'Tag does not match: %s %s'%(self.begin, self.end)

class Sed:
    def __init__(self, comment='#'):
        self.comment = comment

    @staticmethod
    def _split(str, comment):
        sep1 = '(^%s\s*@\w+.*?\s*\n)' %(comment)
        sep2 = '(^%s\s*!<(?:\w+).*?^%s (?:\w+)>!\s*\n)' %(comment, comment)
        sep = '%s|%s'%(sep1, sep2)
        sep = re.compile(sep, re.M|re.S)
        return filter(None, re.split(sep, str))
        
    @staticmethod
    def _tag(str, comment):
        tag1 = '^%s\s*@(\w+)(.*)\s*\n' %(comment)
        tag2 = '^%s\s*!<(\w+)(.*)^%s (\w+)>!\s*\n'%(comment, comment)
        tag1 = re.compile(tag1)
        tag2 = re.compile(tag2, re.M|re.S)
        m1 = re.match(tag1, str)
        m2 = re.match(tag2, str)
        if m1:
            tag, content = m1.groups()
            return tag, content
        elif m2:
            begin_tag, content, end_tag = m2.groups()
            if begin_tag != end_tag:
                raise TagNotMatch(begin_tag, end_tag)
            return begin_tag, content
        else:
            return 'normal', str
    
    def gen_chunk(self, str):
        return '%s !<gen\n%s\n%s gen>!\n' %(self.comment, str, self.comment)
    
    def _chunk(self, str):
        chunks = self._split(str, self.comment)
        return [self._tag(str, self.comment) + (str,) for str in chunks]

    def sed(self, str):
        chunk_list = self._chunk(str)
        new_chunk_list = [getattr(self, tag)(content, raw) for tag, content, raw in chunk_list]
        return ''.join(new_chunk_list)

    def update(self, file_name):
        new_file = self.sed(open(file_name).read())
        return update_file(file_name, new_file)
        
    def normal(self, content, raw):
        return raw

    def gen(self, content, raw):
        return ''
