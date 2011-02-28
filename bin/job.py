#!/usr/bin/python2
"""
example usage:
shell $ job.py ans42:111111@gd[46-50],slaves,-master:boot make boot -/{action} db=config  gd04-root-passwd=a
  where action = inspect | raw | run | bg | cat | view 
"""

import sys
import os, os.path
import exceptions
import subprocess
import traceback
import pprint 
import copy
import string, re

class GErr(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'GErr(%s, %s)'%(repr(self.msg), repr(self.obj))
    
class JobException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'JobException: %s: %s'%(repr(self.msg), repr(self.obj))

def shell(cmd):
    #print "shell:%s" % cmd
    ret = subprocess.call(cmd, shell=True)
    sys.stdout.flush()
    if ret != 0: raise GErr('ShellError', ret)

def ashell(cmd):
    #print "ashell:%s" % cmd
    return subprocess.Popen(cmd, shell=True)

def popen(cmd):
#   print "popen:%s" % cmd
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0 or err:
        raise GErr('PopenError: %s\n%s'%(err, out), cmd)
    return out
    
def list_sum(lists):
    result = []
    for list in lists:
        result.extend(list)
    return result

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

def safe_read(path):
    try:
        f = open(path, 'r')
        ret = f.read()
        f.close()
        return ret
    except exceptions.IOError,e:
        return ''
    
def load_kv_config(f, tag="_config"):
    def safe_read(path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except IOError:
            return ''
    content = safe_read(f)
    match = re.match('begin %s(.+) end %s'%(tag, tag), content, re.S)
    if match: content = match.group(1)
    return dict(re.findall(r'^\s*([^#]\S*)\s*=\s*(\S*)\s*$', content, re.M))

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
            raise JobException('illformaled range specifier', specifier)
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
            'raw': "[ -d /tmp/$last_level_dir ] || mkdir /tmp/$last_level_dir; (cd $dir; $cmd; if [ $? == 0 ]; then echo JobSuccess: raw-cmd; else echo JobException: raw-cmd; fi) >/tmp/$last_level_dir/$host.log 2>&1 &",
            'run': "sshpass -p '$passwd' scp -r $dir $user@$host:; sshpass -p '$passwd' ssh $user@$host '. .bashrc; cd $last_level_dir; $cmd'",
            'bg': "[ -d /tmp/$last_level_dir ] || mkdir /tmp/$last_level_dir; (sshpass -p '$passwd' scp -r $dir $user@$host:; sshpass -p '$passwd' ssh $user@$host '. .bashrc; cd $last_level_dir; $cmd'; if [ $? == 0 ]; then echo JobSuccess: ssh-cmd; else echo JobException: ssh-cmd;fi ) >/tmp/$last_level_dir/$host.log 2>&1",
            'cat': "echo -e '\n-----$host-----\n'; tail -n 100 /tmp/$last_level_dir/$host.log",
            'view':  "tail -n 100 /tmp/$last_level_dir/$host.log",
            }

    def shell(self, cmd):
        def safe_shell(cmd):
            try:
                return shell(cmd)
            except GErr as e:
                print("JobException: shell failed" + str(e))
        return [(p['host'], safe_shell(msub(cmd,p))) for p in self.get_host_profile()]

    def popen(self, cmd):
        def safe_popen(cmd):
            try:
                return popen(cmd)
            except GErr as e:
                return "JobException: popen failed" + str(e)
        return [(p['host'], safe_popen(msub(cmd,p))) for p in self.get_host_profile()]

    def ashell(self, cmd):
        def safe_ashell(cmd):
            try:
                return ashell(cmd)
            except GErr as e:
                print("JobException: shell failed" + str(e))
        return [(p['host'], safe_ashell(msub(cmd,p))) for p in self.get_host_profile()]

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
        return self.shell(self.actions['bg'] + " &")
        
    def wait(self):
        return [(h, p and p.wait()) for h,p in self.ashell(self.actions['bg'])]
    
    def cat(self):
        return self.shell(self.actions['cat'])
    
    def view(self):
        row_pat = '''<tr>
<td style="background:%s; color:white; font-weight:bold">%s</td>
<td><pre>%s</pre></td>
</tr>'''
        def host_bg(output):
            bg_colors = (('green', 'black'), ('red', 'red'))
            return bg_colors[output.find('JobException:') != -1][output.find('JobSuccess:') != -1]
        def output_view(output):
            return re.sub("(JobException:.*\n)", '<div style="color:red">\\1</div>', output, re.M)
        result = [row_pat%(host_bg(output), host, output_view(output)) for host,output in self.popen(self.actions['view'])]
        return "<table border=1>%s</table>" % '\n'.join(result)
    
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
        self.db_vars = load_kv_config(self.db, 'job_db')

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
    except JobException as e:
        print(e)
        print(globals()['__doc__'])
        return
    except exceptions.Exception as e:
        print("Internal Error")
        print(traceback.format_exc())
        return
    job = Job(args.user, args.hosts, args.dir, args.cmd, args.env)
    return getattr(job, args.action)()
    
if __name__ == '__main__':
    print(run_job(sys.argv[1:]))
