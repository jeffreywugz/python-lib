'''
file, process, thread, timer
'''
import sys, os, os.path
import re
import subprocess
from collections import OrderedDict
import fcntl

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
    
def locked_write(path, content):
    with open(path, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(content)
        fcntl.flock(f, fcntl.LOCK_UN)

def mkdir(path):
    os.path.exists(path) or os.mkdir(path)
    
def bg(cmd, output):
    with open(output, 'w') as f:
      return subprocess.Popen(cmd, shell=True, stdin=None, stdout=f, stderr=f)
    
def daemon(func, *args, **kw_args):
    pid = os.fork()
    if pid: return
    pid = os.fork()
    if pid: sys.exit()
    os.setsid()
    func(*args, **kw_args)
    sys.exit()

def interval_times(interval):
    while True:
        yield time.time()
        time.sleep(interval)

class KVFile:
    def __init__(self, path):
        self.path = path
        self.fd = open(path, 'rw')
        self.locked = False

    def __del__(self):
        self.fd.close()
        
    def load(self):
        self.fd.seek()
        return OrderedDict(re.findall(r'^\s*([^#]\S*)[ \t]*=[ \t]*(.*?)$', self.fd.read(), re.M))

    def dump(self, pairs):
        self.lock()
        self.fd.seek()
        self.fd.writelines(['%s = %s\n'%(k,v) for k,v in pairs.items()])
        self.fd.truncate()
        self.unlock()

    def get(self, key, default=None):
        return self.load().get(key, default)

    def update(self, _env_={}, **kw):
        d = self.load()
        d.update(_env_, **kw)
        return self.dump(d)

    def lock(self):
        self.locked or fcntl.flock(self.fd, fcntl.LOCK_EX)

    def unlock(self):
        self.locked and fcntl.flock(self.fd, fcntl.LOCK_UN)
        
# def load_kv_config(f, tag="_config"):
#     content = safe_read(f)
#     match = re.match('begin %s(.+) end %s'%(tag, tag), content, re.S)
#     if match: content = match.group(1)
#     return dict(re.findall(r'^\s*([^#]\S*)\s*=\s*(\S*)\s*$', content, re.M))

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

def table_load(path):
    lines = [line.split() for line in readlines(path)]
    return lines[0], lines[1:]

def log_read(path, *h):
    header, data = table_load(path)
    cols = [header.index(h) for c in cols]
    if any([c == -1 for c in cols]): raise HmonErr('no such cols', cols)
    return [seq_slice(row, *cols) for row in data]

def log_write(path, times, *collectors):
    if os.path.exists(path): raise HmonErr('log file already exists', path)
    f = open(path, 'a')
    f.write('\t'.join(['timestamp'] + list_merge(*[c.values for c in collectors])) + '\n')
    for t in times:
        f.write('\t'.join([str(t)]+ list_merge(*[c() for c in collectors])) + '\n')
        f.flush()
    f.close()

import ctypes
  
libc = ctypes.CDLL(None)
strlen = libc.strlen
strlen.argtypes = [ctypes.c_void_p]
strlen.restype = ctypes.c_size_t
  
memset = libc.memset
memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
memset.restype = ctypes.c_void_p
  
PR_SET_NAME = 15
PR_GET_NAME = 16
  
prctl = libc.prctl
prctl.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong] # we don't want no type safety
prctl.restype = ctypes.c_int
  
def _get_argc_argv():
    argv = ctypes.POINTER(ctypes.POINTER(ctypes.c_char))()
    argc = ctypes.c_int()
    ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))
    return (argc, argv)
  
def getprocname():
    argc, argv = _get_argc_argv()
    return ctypes.cast(argv[0], ctypes.c_char_p).value
  
def setprocname(name):
    argc, argv = _get_argc_argv()
    libc.strncpy(argv[0], name, len(name))
    next = ctypes.addressof(argv[0].contents) + len(name)
    nextlen = strlen(next)
    libc.memset(next, 0, nextlen)
    if prctl(PR_SET_NAME, name, 0, 0, 0) != 0:
        raise OSError()
