import sys, os, os.path
import exceptions
import subprocess

class GErr(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)


def sub(template, **vars):
    return string.Template(template).safe_substitute(**vars)

def msub(template, **env):
    old = ""
    cur = template
    while cur != old:
        old = cur
        cur = sub(cur, **env)
    return cur


def dcmul(*args):
    def _dcmul(a,b):
        return [i + [j] for i in a for j in b]
    return reduce(_dcmul, args, [[]])

def dcmap(func, *args):
    list = dcmul(*args)
    return map(lambda x:func(*x), list)
    
def dmerge(*dicts):
    return reduce(lambda a,b: a.update(b) or a, dicts, {})

def dmap(func, *dicts):
    list = dcmap(dmerge, *dicts)
    return map(func, list)
    
def lset(list, name, func):
    return [i.update(**{name:func(i)}) for i in list]

def lquery(list, **kw):
    def match(item, kw):
        return set(kw.items()) <= set(item.items())
    return filter(lambda x: match(x, kw), list)


def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except exceptions.IOError:
        return ''

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
class Store:
    def __init__(self, path, default_value=None):
        self.path, self.default_value = path, default_value

    def set(self, value):
        f = open(self.path, 'w')
        f.write(repr(value))
        f.close()

    def get(self):
        try:
            f = open(self.path)
            value = eval(f.read())
            f.close()
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

def cmd_args_parse(args):
    splited_args = [i.split('=', 1) for i in args]
    list_args = [i[0] for i in splited_args if len(i)==1]
    kw_args = dict([i for i in splited_args if len(i)==2])
    return list_args, kw_args

def cmd_run(env, args):
    list_args, kw_args = cmd_args_parse(args)
    func = list_args[0]
    func = eval(func, env)
    if not callable(func): raise merr.GErr("not callable", func)
    return func(*list_args[1:], **kw_args)

def mkdir(dir):
    if not os.path.exists(dir): os.mkdir(dir)

def get_ext(name):
    index = name.rfind('.')
    if index == -1: return ""
    return name[index+1:].lower()


def daemonize(stdout_file, stderr_file):
    # os.setsid()
    # os.chdir('/')
    os.umask(0)
    stdin_fd = os.open('/dev/zero', os.O_RDONLY)
    stdout_fd = os.open(stdout_file, os.O_WRONLY|os.O_CREAT)
    stderr_fd = os.open(stderr_file, os.O_WRONLY|os.O_CREAT)
    sys.stdout.flush()
    sys.stderr.flush()
    os.dup2(stdin_fd, 0)
    os.dup2(stdout_fd, 1)
    os.dup2(stderr_fd, 2)

class Daemon:
    def __init__(self, cmd, log_dir):
        self.cmd, self.log_dir = cmd, log_dir
        mkdir(log_dir)
        self.host = get_hostname()
        self.pid_file = self.gen_name('pid')

    def gen_name(self, name):
        return gen_name(os.path.join(self.log_dir, name), self.host)
    
    def start(self):
        pid = self.get_pid()
        if pid == -1:
            stdout_file = self.gen_name('stdout')
            stderr_file = self.gen_name('stderr')
            print "Daemon start process: %s"%(self.cmd)
            daemonize(stdout_file, stderr_file)
            p=subprocess.Popen(self.cmd, shell=True)
            self.set_pid(p.pid)
        else:
            print "Daemon already started!:%d"% pid
        
    def stop(self):
        pid = self.get_pid()
        if pid == -1:
            print "Daemon: no running process found!"
        else:
            print "Daemon: kill process %d!"%(pid)
            os.kill(pid, 9)

    def restart(self):
        self.stop()
        self.start()

    def set_pid(self, pid):
        f = open(self.pid_file, 'w')
        f.write(str(pid))
        f.close()

    def get_pid(self):
        try:
            f = open(self.pid_file, 'r')
            pid = f.read()
            f.close()
        except exceptions.IOError:
            return -1
        if os.path.exists(os.path.join('/proc', pid)):
            return int(pid)
        else:
            return -1

    
