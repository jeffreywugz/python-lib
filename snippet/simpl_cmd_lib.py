def parse_cmd_args(args):
    splited_args = [i.split('=', 1) for i in args]
    list_args = [i[0] for i in splited_args if len(i)==1]
    kw_args = dict([i for i in splited_args if len(i)==2])
    return list_args, kw_args

def make_cmd_args(*list_args, **kw_args):
    args_repr = [repr(arg) for arg in list_args]
    kw_repr = ['%s=%s'%(k, repr(v)) for k,v in kw]
    return args_repr + kw_repr

def cmd_eval(env, func, *list_args, **kw_args):
    try:
        func = eval(func, env)
    except exceptions.IndexError:
        raise GErr('run_cmd(): need to specify a callable object.', args)
    if not callable(func):
        if list_args or kw_args: raise GErr("not callable", func)
        else: return func
    return func(*list_args, **kw_args)

def cmd_app_run(env, func, args, init=''):
    list_args, kw_args = parse_cmd_args(args)
    if kw_args.has_key('--init'):
        init = kw_args['--init']
        del kw_args['--init']
    exec init in env
    new_env = copy.copy(env)
    new_env.update(locals())
    result = cmd_eval(new_env, func, *list_args, **kw_args)
    return result

