import sys, os
from functools import reduce
my_lib_dir = os.path.dirname(os.path.abspath(__file__))
import copy
import re
import subprocess
import time
import string
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
        
def safe_eval(expr, globals={}, locals={}, default=None):
    try:
        return eval(expr, globals, locals)
    except Exception as e:
        return default
    
class Env(dict):
    def __init__(self, d={}, **kw):
        dict.__init__(self)
        self.update(d, **kw)

    def __getattr__(self, name):
        return self.get(name)

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
        
def shell(cmd):
    ret = subprocess.call(cmd, shell=True)
    sys.stdout.flush()
    return ret

def popen(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate() 
    if p.returncode != 0 or err:
        raise GErr('%s\n%s'%(err, out), cmd)
    return out
    
def safe_popen(cmd):
    try:
        return popen(cmd)
    except GErr as e:
        return "Error:\n" + str(e)
        
def read(path):
    with open(path, 'r') as f:
        return f.read()
    
def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except IOError:
        return ''

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
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
