from funclib import *
import re, string

def li(format='%s', sep=' '):
    return lambda seq: sep.join([format% i for i in seq])

def sub2(_str, env=globals(), **kw):
    """Example: $abc ${abc} ${range(3)|> joiner()}"""
    def pipe_eval(ps, env):
        return reduce(lambda x,y: y(x), [safe_eval(p, env) for p in ps.split('|>')])
    return re.sub('(?s)\$(\w+)|\$(?:{(.+?)})', lambda m: str(pipe_eval(m.group(2) or m.group(3), dict_updated(env, kw))), _str)
    
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

def str2dict2(tpl, str):
    rexp = re.sub('\(\w+=(.*?)\)', r'(\1)', tpl)
    keys = re.findall('\((\w+)=.*?\)', tpl)
    print rexp, keys
    match = re.match(rexp, str)
    if not match: return {}
    else: return dict(zip(keys, match.groups()), __self__=str)
    
def tpl_sub(tpl, target, str):
    env = str2dict(tpl, str)
    env.update(_=str)
    return sub(target, env)

def tpl_shell(tpl, cmd, str):
    cmd = tpl_sub(tpl, cmd, str)
    print(cmd)
    shell(cmd)
    

