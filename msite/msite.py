#!/usr/bin/env python

import sys, os
msite_path = os.path.dirname(os.path.abspath(__file__))

import re, exceptions, traceback
import time, datetime
import subprocess
import copy
import cherrypy
from cherrypy.lib import safemime
import wsgiref.handlers
import mako.template
import simplejson as json
import rpc
safemime.init()

class GErr(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

def popen(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    err = p.stderr.read()
    out = p.stdout.read()
    if p.returncode != 0:
        raise GErr('%s\n%s'%(err, out), cmd)
    return out

class Template:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def render(self, templateFileName, **kw):
        path = os.path.join(self.base_dir, templateFileName)
        return mako.template.Template(filename=path).render(**kw)

def render(path, vars={}, **kw_args):
    vars.update(kw_args)
    return mako.template.Template(filename=path).render(**vars)
    
def psh(globals):        
    @rpc.funcWrapper
    def shell(expr='"True"'):
        result = None
        exception = None
        try:
            result = eval(expr, globals, {})
        except exceptions.Exception,e:
            exception = str(e)
        return [result, exception, traceback.format_exc(10)]
    return shell

class Files:
    def __init__(self, base_dir='.'):
        self.base_dir = base_dir

    def gen_path(self, path):
        return os.path.join(self.base_dir, path)

    @cherrypy.expose
    def get(self, path):
        path = self.gen_path(path)
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        try:
            with open(path) as f:
                return f.read()
        except exceptions.IOError:
            return ""
        
    @cherrypy.expose
    def set(self, path, content):
        path = self.gen_path(path)
        with open(path, 'w') as f:
            return f.write(content)

    @cherrypy.expose
    def list(self):
        return json.dumps(os.listdir(self.base_dir))
        
class Root:
    def __init__(self):
        pass
        
    @cherrypy.expose
    def index(self):
        return str(self)

    @rpc.methodWrapper
    def counter(self):
        try:
            cherrypy.session['m_counter'] += 1
        except exceptions.KeyError:
            cherrypy.session['m_counter'] = 0
        return cherrypy.session['m_counter']

    def __str__(self):
        return str(self.__dict__.keys())

m_config = {
    '/jsh':{'tools.staticfile.on': True, 'tools.staticfile.filename': os.path.join(msite_path, 'jsh.html')},
    '/m.css':{'tools.staticfile.on': True, 'tools.staticfile.filename': os.path.join(msite_path, 'm.css')},
    '/m.js':{'tools.staticfile.on': True, 'tools.staticfile.filename': os.path.join(msite_path, 'm.js')},
    '/jsh.js':{'tools.staticfile.on': True, 'tools.staticfile.filename': os.path.join(msite_path, 'jsh.js')},
    '/':{'tools.sessions.on': True},
}

def merge_config(c1, c2):
    c = copy.copy(c1)
    for k,v in c2.items():
        try:
            c[k].update(v)
        except exceptions.KeyError:
            c[k] = v
    return c

def server_start(host='0.0.0.0', port=8080):
    cherrypy.server.socket_host = host
    cherrypy.server.socket_port = port
    cherrypy.engine.start()

def run_as_cgi():
    wsgiref.handlers.CGIHandler().run(cherrypy.tree)

if __name__ == '__main__':
    root = Root()
    root.psh = psh(globals())
    root.files = Files('.')
    root.rpc = rpc.RpcDemo()
    cherrypy.tree.mount(root, '/', config=m_config)
    server_start()
