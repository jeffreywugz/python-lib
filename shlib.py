import os, os.path
import re
from glob import glob
from mako.template import Template

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
    
