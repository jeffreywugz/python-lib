from lazy_man import *

def _c_dep(src, cppflags):
    cmd = "cpp -M -MM -MG %s -MT %s %s"%(cppflags, ext(src, 'o')[0], src)
    output = Popen(cmd, shell=True, stdout=PIPE).communicate()[0]
    target, deps = output.split(':')
    deps = deps.replace('\\', '').split()
    return StaticRule(target, deps)
    
def c_dep(srcs, cppflags):
    return [_c_dep(src, cppflags) for src in list_(srcs)]

c_env = dict(cc='gcc', ld='ld',
             include='include', cppflags='-I. -Iinclude',
             cflags='-g -Wall -Werror', ldflags='')

def get_funcs(str):
    func_list = re.findall('^(.*?) (\w+)\((.*?)\)\s*\n{(.*?)^}', str, re.M|re.S)
    def args_slots(args):
        return [i.split()[-1] for i in args.split(',')]
    return [{'return': _return, 'name':name, 'args': args,  'args_slots': args_slots(args), 'body': body} for _return, name, args, body in func_list]

def get_structs(str):
    struct_list = re.findall('^(?:typedef )?struct (\w+) {\n(.*?)^}', str, re.M|re.S)
    return [{'name': name, 'body':body} for name, body in struct_list]
    
def cprj_setup(lm, out, srcs="*.c", **args):
    srcs = files(srcs)
    lm.update(c_env, srcs=srcs, out=out, objs=ext(srcs, 'o'))
    lm.update(args)
    lm.add(
        StaticRule(lm.out, lm.objs, action="$cc $ldflags -o $target $deps"),
        RegexpRule("(.+)\.o", "\\1.c", action="$cc -o $target $cppflags $cflags -c $deps"),
        c_dep(lm.srcs, lm.cppflags),
        )
