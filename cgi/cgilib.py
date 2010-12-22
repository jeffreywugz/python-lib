import os, os.path
import re
import subprocess
from mako.template import Template
cgi_lib_path = os.path.dirname(os.path.abspath(__file__))

def popen(cmd, cwd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    stdout = p.stdout.read().decode('utf-8')
    tags_match = re.findall('</.+?>', stdout, re.S)
    if len(tags_match) < 5:
        stdout = '<pre>%s</pre>'% stdout
    stderr = p.stderr.read().decode('utf-8')
    p.wait()
    return stdout, stderr

def render(_path, **kw):
    return Template(filename=os.path.join(cgi_lib_path, _path)).render(**kw)