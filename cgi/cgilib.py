import os, os.path
import re
import subprocess
from mako.template import Template
cgi_lib_path = os.path.dirname(os.path.abspath(__file__))

def popen(cmd, cwd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    out, err = p.communicate() 
    out, err = out.decode('utf-8'), err.decode('utf-8')
    tags_match = re.findall('</.+?>', stdout, re.S)
    if len(tags_match) < 5:
        stdout = '<pre>%s</pre>'% stdout
    return out, err

def render(_path, **kw):
    return Template(filename=os.path.join(cgi_lib_path, _path)).render(**kw)
