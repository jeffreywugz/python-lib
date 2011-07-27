#!/usr/bin/env python2

import os, os.path
import sys
my_fsh_dir = os.path.dirname(os.path.abspath(__file__))
import re
import traceback
import exceptions
import subprocess
import mimetypes
from cgi import parse_qs
from urllib import quote

def list_merge(*l):
    return reduce(lambda a,b: list(a)+list(b), l, [])

def iters(step, v, predict=bool):
    while predict(v):
        yield v
        v = step(v)
        
class PshException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'PshException(%s, %s)'%(repr(self.msg), repr(self.obj))

class Store:
    def __init__(self, _dict, **kw):
        self.d = dict(_dict, **kw)

    def get(self, path):
        return self.d.get(path)

    def set(self, path, value):
        self.d[path] = value
        
    def ls(self, pat):
        return [k for k in self.d.keys() if re.search(pat, k)]
    
def rpc_encode(result, tb):
    if tb: return 'Exception:\n%s' % (tb)
    else: return 'OK:\n%s' %(result)
    
def get_mime_type(path):
    return mimetypes.guess_type(path)[0] or 'text/plain'

def err_handler(*args):
    return 'text/plain', 'Not Found!'

def list_all_paths(path, index):
    paths = [os.path.join(*p) for p in iters(lambda x: x[:-1], filter(None, path.split('/')))]
    paths = list_merge(*[(os.path.join(p, index), p) for p in paths + ['']])
    return ['/'+p for p in paths]

def py_loader(str):
    pass

def obj_route(obj, paths):
    pass

def make_rpc_handler(store, loader):
    def rpc_handler(path, query, post):
        for p, args in list_all_paths(path, 'index'):
            obj = loader(store.get(p))
            obj, args = obj_route(args)
            return obj(args)

def try_these(handlers, *args):
    for f in handlers:
        ret = f(*args)
        if ret: return ret

def make_app(*handlers):
    def app(path, query, post):
        mime, content = try_these(handlers, path, query, post)
        return ('200 OK', [('Content-Type', mime)]), content
    return app

def make_wsgi_app(app):
    def wsgi_app(env, response):
        size = int(env.get('CONTENT_LENGTH') or '0')
        header, content = app(env.get('PATH_INFO'), parse_qs(env['QUERY_STRING']), env['wsgi.input'].read(size))
        response(*header)
        return content
    return wsgi_app
            
def make_wsgi_server(app, port=8000):
    from wsgiref.simple_server import make_server
    return make_server('', port, app)
    
# if __name__ == '__main__':
#     port= len(sys.argv) == 2 and int(sys.argv[1]) or 8000
#     print "listening on port: ", port
#     make_wsgi_server(make_wsgi_app(app), port).serve_forever()
