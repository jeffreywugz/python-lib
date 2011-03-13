import sys, os
my_lib_dir = os.path.dirname(os.path.abspath(__file__))
import time

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
        
