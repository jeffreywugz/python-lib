#!/usr/bin/env python2
'''
dump.py will get an object from an `YAML' file,
then render a `mako' Template file to stdout.
Usages:
  ./dump.py [config] term key1=val1 key2=val2...
    - `config' normally is a dict object, and `term' is a `mako' template object
      `dump.py' will render the `mako' template with attributes defined by `config'
       and `key1=val1 key2=val2...' list.
    - `config' and `term' is either an object path defined in an `YAML' file
       or just an plain text file.
       in the form of: path/to/yaml/file/path/to/embeded/object
                   or: path/to/text/file
       not existing path such as ':' will be resolved as ''.
    -  when `term' is '', `dump.py' will dump `config' to stdout in `YAML' format.
'''
import sys, os
app_dir = os.path.dirname(os.path.abspath(__file__))
lib_paths = ['yaml.zip', '../lib/yaml.zip']
sys.path.extend([os.path.join(app_dir, path) for path in lib_paths])
import re
import copy
from subprocess import Popen, PIPE, STDOUT
import yaml
from itertools import groupby 
import types

def usages():
    sys.stderr.write(__doc__)
    sys.exit(1)

def dict_map(func, d):
    return dict((k, func(v)) for (k,v) in list(d.items()))

def dict_updated(d, **kw):
    new_dict = copy.copy(d)
    new_dict.update(**kw)
    return new_dict

def dict_match(d, **pat):
    return all(d.get(k) == v for k,v in pat.items())

def attrs_updater(attrs_generator):
    def updater(**kw):
        return dict_updated(kw, **attrs_generator(**kw))
    return updater

def li(format='%s', sep=' '):
    return lambda seq: sep.join([format% i for i in seq])

def sub2(_str, env=globals(), __safe__=False, **kw):
    """Example: $abc ${abc} ${range(3)|> joiner()} `cat a.txt`"""
    def shell_escape(str):
        return re.sub('`(.*?)`', lambda m: "${popen('%s')}"% m.group(1).replace("'", '\''), str)
    def pipe_eval(ps, env):
        return reduce(lambda x,y: y(x), [eval(p, env) for p in ps.split('|>')])
    def handle_repl(m):
        def remove_brace(x):
            return re.sub('^{(.*)}$', r'\1', x or '')
        try:
            expr = remove_brace(m.group(1)) or remove_brace(m.group(2))
            return str(pipe_eval(expr, dict_updated(env, kw)))
        except Exception, e:
            if not __safe__: raise e
            return '$%s'%(m.group(1) or m.group(2))
    return re.sub('(?s)(?<![$])\$(\w+)|\$({.+?})', handle_repl, shell_escape(_str)).replace('$$', '$')

def make_smart_eval_constructor(**env):
    def sub(tpl, **vars):
        return sub2(tpl, **dict_map(dict2env, vars))
    @attrs_updater
    def tpl_sub(_prefix='tpl_', **kw):
        return dict((k[len(_prefix):], sub(v, **kw)) for k,v in kw.items() if k.startswith(_prefix))
    def popen(cmd):
        return Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0].strip()
    env.update(li=li, dict2env=dict2env, sub=sub, popen=popen, dict_updated=dict_updated, tpl_sub=tpl_sub)
    def smart_eval(loader, obj):
        if isinstance(obj, yaml.nodes.MappingNode):
            value = loader.construct_mapping(obj)
        elif isinstance(obj, yaml.nodes.SequenceNode):
            value = loader.construct_sequence(obj)
        else:
            value = obj.value
        if not value: return None
        if type(value) == str or type(value) == unicode:
            if len(value.split('\n')) > 1:
                exec value in env
                return None
            else:
                return eval(value, env)
        elif type(value) == list:
            _value = [i for i in value]
            func = _value[0]
            if type(func) == str or type(func) == unicode: func = eval(func, env)
            return func(*_value[1:])
        elif type(value) == dict:
            _value = dict((k, v) for k,v in value.items())
            func = _value['__func__']
            if type(func) == str or type(func) == unicode: func = eval(func, env)
            del _value['__func__']
            return func(**_value)
        else:
            return value
    return smart_eval
    
class Env(dict):
    def __init__(self, d={}):
        dict.__init__(self, **d)

    def __getattr__(self, name):
        return dict2env(self.get(name))
    
def dict2env(d):
    if type(d) == dict:
        return Env(d)
    else:
        return d

def env2dict(e):
    if type(e) == Env:
        return dict(e.items())
    else:
        return e
    
def read(path):
    with open(path, 'r') as f:
        return f.read()
    
def safe_read(path):
    try:
        return read(path)
    except IOError:
        return ''
    
def dict_updated(d, extra={}, **kw):
    new_dict = copy.copy(d)
    new_dict.update(extra, **kw)
    return new_dict

def parse_cmd_args(args):
    return [i for i in args if not re.match('^\w+=', i)], dict(i.split('=', 1) for i in args if re.match('^\w+=', i))

def parse_arg(args):
    ls_args, kw_args = parse_cmd_args(args)
    inline = ls_args and ls_args[0] or ''
    term = len(ls_args) >= 2 and ls_args[1] or ''
    return term, inline, kw_args

def iter_until_null(func, initial=None, terminate=lambda x: not x):
    while not terminate(initial):
        yield initial
        initial = func(initial)

def lp_exists(path, suffix=''):
    paths = filter(lambda x: os.path.exists(x + suffix), iter_until_null(lambda p: re.sub('/?[^/]*$', '', p), path))
    return paths and paths[0]

def find_attr(obj, path):
    return reduce(lambda obj,attr: getattr(obj, attr, None),  filter(None, path.split('/')), obj)

def load_yaml_obj(path, default):
    yaml_path = lp_exists(path, '.yml') or ''
    yaml_obj = dict2env(yaml.load(safe_read((yaml_path or default) + '.yml')))
    return find_attr(yaml_obj, path[len(yaml_path):]) or {}

def load(path, default=''):
    return safe_read(path) or load_yaml_obj(path, default)

def dump_yaml_obj(obj):
    if type(obj) == str:
        return obj
    else:
        return yaml.dump(obj)

def dump(term, inline, **kw):
    tpl, env = load(term, 'tpl'), env2dict(load(inline, 'config'))
    if tpl:
        if type(env) != dict or (type(tpl) != str and type(tpl) != unicode):
            raise Exception('type error: tpl is not str/unicode %s, env is not dict: %s'%(repr(tpl), repr(env)))
        return sub2(tpl, **dict_updated(dict_map(dict2env, env), **kw))
    else:
        return dump_yaml_obj(env)

if __name__ == '__main__':
    yaml.add_constructor('!e', make_smart_eval_constructor(load=load))
    term, inline, attrs = parse_arg(sys.argv[1:])
    inline or usages()
    print dump(term, inline, **attrs)
