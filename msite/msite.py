#!/usr/bin/env python

import sys, os
msite_path = os.path.dirname(os.path.abspath(__file__))
# sys.path.extend([os.path.join(msite_path, '..')]
from common import *
import re, exceptions, traceback
import time, datetime
import subprocess
import copy
import cherrypy
from cherrypy.lib import safemime
from cherrypy.lib.static import serve_file
import wsgiref.handlers
from mako.template import Template
import simplejson as json
import rpc
safemime.init()

class Files:
    def __init__(self, base_dir='.'):
        self.base_dir = base_dir

    def gen_path(self, path):
        return os.path.join(self.base_dir, path)

    @cherrypy.expose
    def index(self):
        return json.dumps(os.listdir(self.base_dir))

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

    
class Shell:
    def __init__(self, globals):
        self.globals = globals
                                         
    @cherrypy.expose
    def index(self):
        return str(self.globals)
    
    @cherrypy.expose
    def py(self, expr='True'):
        result = None
        exception = None
        try:
            result = eval(expr, self.globals, locals())
        except exceptions.Exception,e:
            exception = e
            result = str(exception)
        return Template(filename=os.path.join(msite_path, 'psh.html')).render(expr=expr, result=result, exception=exception, traceback=traceback.format_exc(10))

    @cherrypy.expose
    def js(self):
        return serve_file(os.path.join(msite_path, 'jsh.html'), content_type='text/html')

    @cherrypy.expose
    def eval(self, expr='True'):
        result = None
        exception = None
        try:
            result = eval(expr, self.globals, {})
        except exceptions.Exception,e:
            exception = str(e)
        return [result, exception, traceback.format_exc(10)]


class Session:
    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        return str(cherrypy.session)
        
    @cherrypy.expose
    def get(self, key):
        return cherrypy.session.get(key, None)

    @cherrypy.expose
    def set(self, key, value):
        cherrypy.session[key] = value

class MsiteApp:
    config = {
        '/m':{'tools.staticdir.on': True, 'tools.staticdir.dir': msite_path},
        '/':{'tools.sessions.on': True},
        }
    def __init__(self, files_dir, rpc, py_env, extra_config={}):
        self.fs = Files(files_dir)
        self.tmp = Session()
        self.rpc = rpc
        self.sh = Shell(py_env)
        self.config = self.merge_config(MsiteApp.config, extra_config)
        cherrypy.tree.mount(self, '/', config=self.config)
        
    @cherrypy.expose
    def index(self):
        return str(self.__dict__.keys())

    def run(self, host='0.0.0.0', port=8080):
        cherrypy.server.socket_host = host
        cherrypy.server.socket_port = port
        cherrypy.engine.start()

    def run_as_cgi(self):
        wsgiref.handlers.CGIHandler().run(cherrypy.tree)
        
    @staticmethod
    def merge_config(c1, c2):
        c = copy.copy(c1)
        for k,v in c2.items():
            try:
                c[k].update(v)
            except exceptions.KeyError:
                c[k] = v
        return c
