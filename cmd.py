from common import *

def filter_cmd_args(args, *opts):
    def getopt(arg):
        for opt in opts:
            prefix = '--%s='%(opt)
            if arg.startswith(prefix): return opt, arg.replace(prefix, '')
        return None, None
    rest_args = filter(lambda arg: getopt(arg) == (None, None), args)
    kw = dict([getopt(arg) for arg in args])
    return rest_args, kw

def parse_cmd_args(args, env):
    def parse_arg(arg):
        if arg.startswith(':'): return (arg,)
        else:  return arg.split('=', 1)
    def eval_arg(arg):
        if not arg.startswith(':'):
            return arg
        try:
            return eval(arg[1:], env)
        except exceptions.Exception,e:
            return GErr("arg %s eval error"%arg, e)
    args = map(parse_arg, args)
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
    exec init in env
    pipes = lsplit(args, '/')
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
    if not callable(func):
        if  list_args or kw_args:
            raise GErr("not callable", func)
        else:
            result = func
    else:
        result = func(*list_args, **kw_args)
    env.update(_=result)
    return result

