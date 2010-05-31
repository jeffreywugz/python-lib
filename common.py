import sys, os, os.path
my_lib_dir = os.path.dirname(os.path.abspath(__file__))
lib_paths = ['.', 'lib/mako.zip', 'lib/simplejson.zip', 'lib/cherrypy.zip']
sys.path.extend([os.path.join(my_lib_dir, path) for path in lib_paths])
import exceptions
import subprocess

class GErr(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

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
        
class Store:
    def __init__(self, path, default_value=None):
        self.path, self.default_value = path, default_value

    def set(self, value):
        with open(self.path, 'w') as f:
            f.write(repr(value))

    def get(self):
        try:
            with open(self.path) as f:
                value = eval(f.read())
        except exceptions.IOError:
            return self.default_value
        return value

class Log:
    def __init__(self, path):
        self.path = path
        self.file = open(path, 'a+', 1)

    def __del__(self):
        self.file.close()
        
    def record(self, *fields):
        list = [time.time()]
        list.extend(fields)
        self.file.write(repr(list)+'\n')

    def get(self):
        lines = self.file.readlines()
        def safe_eval(expr, default):
            try:
                return eval(expr)
            except exceptions.Exception:
                return default
        values = [safe_eval(line, None) for line in lines]
        return filter(None, values)

def parse_cmd_args(args):
    splited_args = [i.split('=', 1) for i in args]
    list_args = [i[0] for i in splited_args if len(i)==1]
    kw_args = dict([i for i in splited_args if len(i)==2])
    return list_args, kw_args

def run_cmd(env, args):
    list_args, kw_args = parse_cmd_args(args)
    try:
        func = list_args[0]
    except exceptions.IndexError:
        raise GErr('run_cmd(): need to specify a callable object.', args)
    func = eval(func, env)
    if not callable(func): raise merr.GErr("not callable", func)
    return func(*list_args[1:], **kw_args)

def shell(cmd):
    print cmd
    ret = subprocess.call(cmd, shell=True)
    sys.stdout.flush()
    return ret

def popen(cmd):
    print cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    err = p.stderr.read()
    out = p.stdout.read()
    if p.returncode != 0 or err:
        raise merr.GErr('%s\n%s'%(err, out), cmd)
    return out

def sub(template, **vars):
    return string.Template(template).safe_substitute(**vars)

def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except exceptions.IOError:
        return ''

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
def gen_name(*parts):
    return '.'.join(parts)

