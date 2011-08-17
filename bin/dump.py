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
lib_paths = ['mako.zip', '../lib/mako.zip', 'yaml.zip', '../lib/yaml.zip']
sys.path.extend([os.path.join(app_dir, path) for path in lib_paths])
import re
import copy
from mako.template import Template
import yaml
from itertools import groupby 

def usages():
    sys.stderr.write(__doc__)
    sys.exit(1)
    
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

def load(path, default):
    return safe_read(path) or load_yaml_obj(path, default)

def dump_yaml_obj(obj):
    if type(obj) == str:
        return obj
    else:
        return yaml.dump(obj)
    
def dump(term, inline, **kw):
    tpl, env = load(term, 'tpl'), load(inline, 'config')
    return (not tpl) and dump_yaml_obj(env2dict(env)) or Template(text=tpl).render(**dict_updated(env, **kw))

if __name__ == '__main__':
    term, inline, attrs = parse_arg(sys.argv[1:])
    inline or usages()
    print dump(term, inline, **attrs)
