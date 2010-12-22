import sys, os
from functools import reduce
my_lib_dir = os.path.dirname(os.path.abspath(__file__))
import copy
import re
import subprocess
import time
import string
from mako.template import Template
from itertools import groupby

class GErr(Exception):
    def __init__(self, msg, obj=None):
        Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'GErr(%s, %s)'%(repr(self.msg), repr(self.obj))

def short_repr(x):
    if len(x) < 80: return x
    else: return x[:80] + '...'
    
def traceit(func):
    def wrapper(*args, **kw):
        args_repr = [repr(arg) for arg in args]
        kw_repr = ['%s=%s'%(k, repr(v)) for k,v in list(kw.items())]
        full_repr = list(map(short_repr, args_repr + kw_repr))
        print('%s(%s)'%(func.__name__, ', '.join(full_repr)))
        result = func(*args, **kw)
        print('=> %s'%(repr(result)))
        return result
    return wrapper

def timeit(func):
    def wrapper(*args, **kw):
        start = time.time()
        result = func(*args, **kw)
        end = time.time()
        print('%s(*%s, **%s): %ds'%(func.__name__, args, kw, end-start))
        return result
    return wrapper

def mktracer(log):
    def tracer(func):
        def wrapper(*args, **kw):
            start = time.time()
            result = func(*args, **kw)
            end = time.time()
            log.record(func.__name__, result, start, end)
            return result
        return wrapper
    return tracer

def print_table(table):
    for i in table:
        print('\t'.join([str(j) for j in i]))
        
def safe_eval(expr, env={}, default=None):
    try:
        return eval(expr, env)
    except Exception as e:
        return default
    
class Env(dict):
    def __init__(self, d={}, **kw):
        dict.__init__(self)
        self.update(d, **kw)

    def __getattr__(self, name):
        return self.get(name)

class TemplateSet:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        
    def render(self, file, **kw):
        return Template(filename=os.path.join(self.base_dir, file)).render(**kw)
        
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
        
class Templet:
    """Example: $abc ${abc} ${' '.join(range(3))}"""
    def __init__(self, str):
        self.str = str

    def sub(self, env={}, **kw):
        preprocessed = re.sub('\$(\w+)', '${\\1}', self.str) # Normalize: 'abc $foo def' => 'abc ${foo} def'
        segments = re.split('(?s)(\${.+?})', preprocessed) # Split into Chunks: 'abc ${foo} def' => ['abc', '${foo}', 'def']
        env.update(**kw)
        def safe_eval(exp, env):
            try:
                return eval(exp, globals(), env)
            except Exception as e:
                return e
        def evil(seg):
            if not re.match('\$', seg): # This is for Normal Chunks.
                return seg
            exp = re.sub('(?s)^\${(.+?)}', '\\1', seg)
            result = safe_eval(exp, env)
            return str(result)
        return ''.join([evil(seg) for seg in segments])
    
def sub(template, env={}, **vars):
    return string.Template(template).safe_substitute(env, **vars)

def msub(template, env={}, **kw):
    old = ""
    cur = template
    new_env = copy.copy(env)
    new_env.update(kw)
    while cur != old:
        old = cur
        cur = sub(cur, new_env)
    return cur

def str2dict(template, str):
    def normalize(str):
        return re.sub('\$(\w+)', r'${\1:\w+}', str)
    def tore(str):
        return re.sub(r'\${(\w+):([^}]+)}', r'(?P<\1>\2)', str)
    rexp = '^%s$' % (tore(normalize(template)))
    match = re.match(rexp, str)
    if not match: return {}
    else: return dict(match.groupdict(), __self__=str)

def tpl_sub(tpl, target, str):
    env = str2dict(tpl, str)
    env.update(_=str)
    return sub(target, env)

def shell(cmd):
    ret = subprocess.call(cmd, shell=True)
    sys.stdout.flush()
    return ret

def popen(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    err = p.stderr.read()
    out = p.stdout.read()
    if p.returncode != 0 or err:
        raise GErr('%s\n%s'%(err, out), cmd)
    return out
    
def safe_popen(cmd):
    try:
        return popen(cmd)
    except GErr as e:
        return "Error:\n" + str(e)
        
def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except IOError:
        return ''

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
def sub_shell(tpl, cmd, str):
    cmd = tpl_sub(tpl, cmd, str)
    print(cmd)
    shell(cmd)
    
def sh_sub(str):
    exprs = re.findall(str, '`([^`])`')
    return reduce(lambda str, expr: str.replace('`%s`'%expr, os.popen(expr)), exprs, str)

def load_kv_config(f, tag="_config"):
    content = safe_read(f)
    match = re.match('begin %s(.+) end %s'%(tag, tag), content, re.S)
    if match: content = match.group(1)
    return dict(re.findall(r'^\s*([^#]\S*)\s*=\s*(\S*)\s*$', content, re.M))

class Log:
    def __init__(self, path):
        self.path = path
        self.file = open(path, 'a+', 1)

    def __del__(self):
        self.file.close()
        
    def clear(self):
        pass
    
    def record(self, *fields):
        list = [time.time()]
        list.extend(fields)
        self.file.write(repr(list)+'\n')

    def get(self):
        lines = self.file.readlines()
        values = [safe_eval(line) for line in lines]
        return [_f for _f in values if _f]
    
core_templates = TemplateSet(os.path.join(my_lib_dir, 'res'))
