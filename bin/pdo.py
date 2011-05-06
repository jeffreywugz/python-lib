#!/usr/bin/python2

"""
pdo which means `pattern do', can be use to do some operation based on a seqence of strings
Usages:
pdo '$base.png' echo '$s $base.jpg' : *.png
pdo '.png->.svg' echo '$s $t' : *.png
"""
import sys
import exceptions
import traceback
import string, re
import subprocess

class PdoException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'PdoException(%s, %s)'%(repr(self.msg), repr(self.obj))
    
def sub(template, env={}, **vars):
    return string.Template(template).safe_substitute(env, **vars)

def li(format='%s', sep=' '):
    return lambda seq: sep.join([format% i for i in seq])

def sub2(_str, env=globals(), **kw):
    """Example: $abc ${abc} ${range(3)|> joiner()}"""
    def pipe_eval(ps, env):
        return reduce(lambda x,y: y(x), [safe_eval(p, env) for p in ps.split('|>')])
    return re.sub('(?s)\$(\w+)|\$(?:{(.+?)})', lambda m: str(pipe_eval(m.group(2) or m.group(3), dict_updated(env, kw))), _str)

def shell(cmd):
    return subprocess.call(cmd, shell=True)

def parse(args):
    def get_colon_index(args):
        for i,v in enumerate(args):
            if v.startswith(':'): return i
        raise PdoException('Missing ":" in args', args)
    def split_by_colon(args):
        i = get_colon_index(args)
        return args[:i], args[i+1:]
    def normalize(str):
        return re.sub('\$(\w+)', r'${\1:\w+}', str)
    def src2re(str):
        return re.sub(r'\${(\w+):([^}]+)}', r'(?P<\1>\2)', str)
    def repl2re(str):
        return re.sub(r'\$(\w+)', r'\\g<\1>', str)
    head, items = split_by_colon(args)
    if not head: raise PdoException('Missing pattern before ":"', head)
    pat, cmd = head[0], head[1:]
    pat = pat.split('->')
    if len(pat) > 2: raise PdoException("`->' appeared more than once")
    if len(pat) < 2: pat.append('')
    [src, target] = pat
    return [src2re(normalize(src)), repl2re(target)], ' '.join(cmd), items

def tpl_sub((src, target), tpl, str):
    env = re.search(src, str)
    if not env: return None
    env = env.groupdict()
    target = re.sub(src, target, str)
    env.update(s=str, t=target)
    return sub(tpl, env)
        
def pdo_cmds((src, target), tpl, items):
    return filter(None, [tpl_sub([src, target], tpl, i) for i in items])

def main(args):
    try:
        for cmd in pdo_cmds(*parse(args)): shell(cmd)
    except PdoException as e:
        print(e)
        print(globals()['__doc__'])
    except exceptions.Exception as e:
        print("Internal Error")
        print(traceback.format_exc())
        return

if __name__ == '__main__':
    main(sys.argv[1:])
