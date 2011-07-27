#!/usr/bin/env python2
'''
Usage:
./task.py 'cmd # res-reqs' [top-dir]
<top-dir> defaults to: tasks
Example:
./task.py 'sleep 10; echo done # cpu=cpu*:3
'''
import sys, os, os.path
import re
import time
import random
import subprocess
import fcntl
import signal
from glob import glob

def list_merge(*l):
    return reduce(lambda a,b: list(a)+list(b), l, [])

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
    
def mkdir(path):
    os.path.exists(path) or os.mkdir(path)
    
def bg(cmd, output, env={}, cleanup=None):
    new_env = dict(os.environ, **env)
    with open(output, 'w') as f:
        p = subprocess.Popen(cmd, shell=True, stdin=None, stdout=f, stderr=f, env=new_env)
        def term_handler(sig, frame):
            if cleanup: cleanup(p.pid)
            sys.exit()
        [signal.signal(sig, term_handler) for sig in (signal.SIGABRT, signal.SIGHUP, signal.SIGINT, signal.SIGTERM)]
        return p
    
def daemon(func, *args, **kw_args):
    pid = os.fork()
    if pid: return
    os.setsid()
    pid = os.fork()
    if pid: sys.exit()
    func(*args, **kw_args)
    sys.exit()

def interval_times(interval):
    while True:
        yield time.time()
        time.sleep(interval)

def lockf_nb(fd):
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError,e:
        return False
    
def try_lock_files(files):
    fds = [open(path, 'w') for path in files]
    if all(lockf_nb(fd) for fd in fds):
        return fds
    else:
        [fd.close() for fd in fds]
        return None

def lock_some_files(reqs, interval=1):
    reqs = [(k, glob(pat), count) for k, pat,count in reqs]
    for i in interval_times(interval):
        selected = [(k, random.sample(files, count)) for k,files,count in reqs]
        selected_files = list_merge(*[files for k,files in selected])
        fds = try_lock_files(selected_files)
        if fds != None: return selected, fds

def task_execute(cmd, env, outfile, codefile):
    env = dict((k,','.join(v)) for k,v in env.items())
    code = bg(cmd, outfile, env, cleanup=lambda pid: os.kill(pid, signal.SIGTERM)).wait()
    write(codefile, str(code))
    
def task_start(notify, work_dir, cmd, res_req):
    mkdir(work_dir)
    lockfile, outfile, codefile = work_dir+'/lock', work_dir+'/output', work_dir+'/code'
    with open(lockfile, 'w') as fd:
        if not lockf_nb(fd):
            notify()
            return 'busy'
        if safe_read(codefile) == '0':
            notify()
            return 'done'
        files, fds = lock_some_files(res_req)
        notify()
        res = [(k,map(os.path.basename, fs)) for k,fs in files]
        task_execute(cmd, dict(filter(lambda (k,fs):k, res)), outfile, codefile)
        return 'started'

def task_start_helper(top_dir, cmd):
    def safe_int(x, default=1):
        try:
            return int(x)
        except ValueError:
            return 1
    def slugify(x):
        return re.sub('[/ ]', '-', x)
    m = re.match('^.+#(.*)$', cmd)
    if m: res_reqs = m.group(1)
    else: res_reqs = ''
    res_reqs = re.findall('(?:(\w+)=)?([^: ]+)(?::(\d+))?', res_reqs)
    res_reqs = [(k,'%s/res/%s'%(top_dir, pat), safe_int(count)) for k,pat,count in res_reqs]
    _pid = os.getpid()
    def notify():
        os.kill(_pid, signal.SIGALRM)
    pid = os.fork()
    if pid:
        signal.pause()
    else:
        time.sleep(1) # to make sure child not exit after parent call signal.pause()
        daemon(task_start, notify, '%s/%s'%(top_dir, slugify(cmd)), cmd, res_reqs)

if __name__ == '__main__':
    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    cmd, top_dir = sys.argv[1], len(sys.argv) == 3 and sys.argv[2] or 'tasks'
    print task_start_helper(top_dir, cmd)
    
    
