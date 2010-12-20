from common import *
import exceptions
import collections
import os, os.path
import re
from glob import glob

# Shell 2 Python Interface
def cmd_arg_quote(arg):
    return '"%s"'%(arg.replace('"', '\\"').replace('$', '\\$'))

def filter_cmd_args(args, *opts):
    def getopt(arg):
        for opt in opts:
            prefix = '--%s='%(opt)
            if arg.startswith(prefix): return opt, arg.replace(prefix, '')
        return None, None
    rest_args = [arg for arg in args if getopt(arg) == (None, None)]
    kw = dict([getopt(arg) for arg in args])
    return rest_args, kw

def make_cmd_args(*args, **kw):
    args_repr = [repr(arg) for arg in args]
    kw_repr = ['%s=%s'%(k, repr(v)) for k,v in list(kw.items())]
    return ' '.join(args_repr + kw_repr)
    
def parse_cmd_args(args, env):
    def parse_arg(arg):
        if (not arg.startswith(':')) and re.match('\S+=', arg): return arg.split('=', 1)
        else: return (arg,)
    def eval_arg(arg):
        if arg.startswith('::'): return arg[1:]
        if not arg.startswith(':'): return arg
        try:
            return eval(arg[1:], env)
        except exceptions.Exception as e:
            return GErr("arg %s eval error"%arg, e)
    args = list(map(parse_arg, args))
    args = [(k, list(iters)) for k,iters in groupby(sorted(args, key=len), key=len)]
    args = dict(args)
    list_args = args.get(1, [])
    kw_args = args.get(2, [])
    list_args = [eval_arg(i) for (i,) in list_args]
    kw_args = dict([(k, eval_arg(v)) for (k,v) in kw_args])
    return list_args, kw_args

def run_cmd(env, args):
    args, opts = filter_cmd_args(args, 'init')
    init = opts.get('init', '')
    exec(init, env)
    pipes = list_split(args, '/')
    for p in pipes[1:]:
        if not (':_' in p or any([i.endswith('=:_') for i in p])):
            p.append(':_')
    results = [cmd_pipe_eval(env, p) for p in pipes]
    return results[-1]

def cmd_pipe_eval(env, args):
    list_args, kw_args = parse_cmd_args(args[1:], env)
    try:
        func = args[0]
    except exceptions.IndexError:
        raise GErr('run_cmd(): need to specify a callable object.', args)
    func = eval(func, env)
    if not isinstance(func, collections.Callable):
        if  list_args or kw_args:
            raise GErr("not callable", func)
        else:
            result = func
    else:
        result = func(*list_args, **kw_args)
    env.update(_=result)
    return result

# Python 2 Shell interface
def gen_name(*parts):
    return '.'.join(parts)

def get_ext(name):
    index = name.rfind('.')
    if index == -1: return ""
    return name[index+1:].lower()

def file_extract(f, pattern):
    content = safe_read(f)
    match = re.search(pattern, content)
    if match: return match.groups()
    else: return []

def mkdir(dir):
    if not os.path.exists(dir): os.mkdir(dir)

def rmrf(target):
    shell('rm -rf %s'%target)
    
def gen_file(env, tpl, file):
    new_content = Template(filename=tpl).render(**env)
    write(file, new_content)
    
