#!/usr/bin/python
"""
example usage:
bash$ job.py root:111111@gd[46-50],slaves,-master:/share/work/boot make ok -/passrun db=config gd04-root-passwd=a
"""

import sys
import os, os.path
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.join(cwd, '..')])
from common import *
import exceptions
import traceback
import pprint 
import copy
import string, re

class JobException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'JobException(%s, %s)'%(repr(self.msg), repr(self.obj))

        
def cmd_arg_quote(arg):
    return arg
    # return '%s'%(arg.replace('"', '\\"'))

def gen_list(*ranges):
    def parse(i):
        if re.match('[-+]', i): type,i = i[0], i[1:]
        else: type = '+'
        match = re.search(r'\[(.+)\]', i)
        if not match:
            return type, [i]
        specifier = match.group(1)
        match = re.match('([0-9]+)-([0-9]+)', specifier)
        if not match:
            raise GErr('illformaled range specifier', specifier)
        _start, _end = match.groups()
        start,end = int(_start), int(_end)
        formatter = re.sub('\[.+\]', '%0'+str(len(_start))+'d', i)
        return type, [formatter%(x) for x in range(start, end+1)]
    ranges = [parse(i) for i in ranges]
    included = [r for t, r in ranges if t == '+']
    excluded = [r for t, r in ranges if t == '-']
    included,excluded = list_sum(included), list_sum(excluded)
    ranges = set(included) - set(excluded)
    return sorted(list(ranges))
    
class Job:
    def __init__(self, user, hosts, dir, cmd, env):
        self.user, self.hosts, self.dir, self.cmd, self.env = user, hosts, dir, cmd, env
        self.actions = {
            'raw': "[ -d /tmp/$last_level_dir ] || mkdir /tmp/$last_level_dir; cd $dir; $cmd >/tmp/$last_level_dir/$host.log 2>&1 &",
            'run': "sshpass -p '$passwd' scp -r $dir $user@$host:; sshpass -p '$passwd' ssh $user@$host '. .bashrc; cd $last_level_dir; $cmd'",
            'bg': "[ -d /tmp/$last_level_dir ] || mkdir /tmp/$last_level_dir; (sshpass -p '$passwd' scp -r $dir $user@$host:; sshpass -p '$passwd' ssh $user@$host '. .bashrc; cd $last_level_dir; $cmd') >/tmp/$last_level_dir/$host.log 2>&1 &",
            'cat': "echo -e '\n-----$host-----\n'; tail -n 100 /tmp/$last_level_dir/$host.log",
            'view':  "tail -n 100 /tmp/$last_level_dir/$host.log",
            }

    def shell(self, cmd):
        return [(p['host'], shell(msub(cmd,p))) for p in self.get_host_profile()]

    def popen(self, cmd):
        return [(p['host'], safe_popen(msub(cmd,p))) for p in self.get_host_profile()]
    
    def get_host_profile(self):
        return [dict(host=h, user=self.user, dir=self.dir,
                     passwd=self.env.get('%s-%s-passwd'%(h, self.user), ''),
                     cmd=' '.join([cmd_arg_quote(msub(i, self.env)) for i in self.cmd]),
                     last_level_dir=os.path.basename(self.dir)) for h in self.hosts]

    def raw(self):
        return self.shell(self.actions['raw'])
    
    def run(self):
        return self.shell(self.actions['run'])
    
    def bg(self):
        return self.shell(self.actions['bg'])
    
    def cat(self):
        return self.shell(self.actions['cat'])
    
    def view(self):
        return ''.join(['<h3>%s</h3>\n<pre>%s</pre>\n'%(host, output) for host,output in self.popen(self.actions['view'])])
    
    def inspect(self):
        return self.get_host_profile()
    
    def __str__(self):
        return 'Job(user=%s, hosts=%s, dir=%s, cmds=%s, env=...)'%(self.user, self.hosts, self.dir, self.cmds)

class JobParser:
    def __init__(self, args):
        self.args = args
        self.default_action, self.default_db = 'view', 'job.db'
        self.parse()
        
    def parse(self):
        def get_action_index(args):
            for i,v in enumerate(args):
                if v.startswith('-/'): return i
            return -1
        def split_by_action(args, default_action):
            i = get_action_index(args)
            if i == -1: return args, default_action, []
            return args[:i], args[i][2:], args[i+1:]
        def parse_job(job):
            pattern = r'([^:@]+):?(\S*)@(\S+):(\S+)$'
            match = re.search(pattern, job)
            if not match: raise JobException('job-spec parse Error', job)
            user, passwd, hosts, dir = match.groups()
            hosts = hosts.split(',')
            return user, passwd, hosts, dir
        
        def parse_hosts(hosts, vars):
            def replace(h, vars):
                match = re.match('([-+]?)(.*)', h)
                prefix, h = match.groups()
                return [prefix+i for i in vars.get(h, h).split(',')]
            hosts = [replace(h, vars) for h in hosts]
            hosts = list_sum(hosts)
            return gen_list(*hosts)
            
        def make_passwd_vars(hosts, user, passwd):
            return dict([('%s-%s-passwd'%(h, user), passwd) for h in hosts])

        job, self.action, cmd_vars = split_by_action(self.args, self.default_action)
        self.cmd_vars = dict([i.split('=', 1) for i in cmd_vars])
        self.db = self.cmd_vars.get('db', self.default_db)
        self.db_vars = load_kv_config(self.db)

        if not job: raise JobException('Wrong Arguments')
        self.user, self.default_passwd, hosts, self.dir = parse_job(job[0])
        self.cmd = job[1:]
        self.hosts = parse_hosts(hosts, self.db_vars)
        self.env = make_passwd_vars(self.hosts, self.user, self.default_passwd)
        self.env.update(self.db_vars, **self.cmd_vars)
    
    def __str__(self):
        return '''
JobParser(args=%s):
    action=%s
    user=%s
    hosts=%s
    dir=%s
    cmd=%s
    db=%s
    db_vars=%s
    cmd_vars=%s
    env=%s
'''%(self.args, self.action, self.user, self.hosts, self.dir, self.cmd, self.db, self.db_vars, self.cmd_vars, self.env)

def run_job(args):
    try:
        args = JobParser(args)
    except JobException,e:
        print e
        print """
Examples:
shell $ job.py ans42:111111@gd[46-50]:boot make boot -/{action} db=config
where action = inspect | raw | run | bg | cat | view 
"""
        return
    except exceptions.Exception,e:
        print "Internal Error"
        print traceback.format_exc()
        return
    job = Job(args.user, args.hosts, args.dir, args.cmd, args.env)
    return getattr(job, args.action)()
    
if __name__ == '__main__':
    print run_job(sys.argv[1:])
