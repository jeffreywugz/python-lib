#!/usr/bin/env python2

import os, os.path
import sys
my_fsh_dir = os.path.dirname(os.path.abspath(__file__))
import traceback
import mimetypes
from cgi import parse_qs
from urllib import quote
import wsgiref.handlers

def get_mime_type(path):
    return mimetypes.guess_type(path)[0] or 'text/plain'

def listdir(path):
    files = [(i,os.path.join(path, i)) for i in ['..']+sorted(os.listdir(path))]
    files = [(name, path, ['', '/'][os.path.isdir(path)]) for name, path in files]
    files = [(name+slash, path+slash) for name,path,slash in files]
    files = ['<li><a href="%s"><pre>%s</pre></a>'%(quote(path), name) for name, path in files]
    return '<style type="text/css">pre{margin-top:0; margin-bottom:0;} pre:hover{background-color: red;}</style><ul>%s</ul>' % '\n'.join(files)

def read(path):
    with open(path) as f:
        return f.read()

def safe_read(path):
    try:
        return read(path)
    except Exception:
        pass
    
def serve_file(path):
    content = safe_read(path)
    if content: return get_mime_type(path), content

def try_these(handlers, *args):
    for f in handlers:
        ret = f(*args)
        if ret: return ret

def err_handler(*args):
    return 'text/plain', 'Not Found!'

def index_handler(path, *args):
    return serve_file(os.path.join(path, 'index.html'))

def dir_handler(path, *args):
    if os.path.isdir(path): return 'text/html', listdir(path)

def file_handler(path, *args):
    return serve_file(path)

def first_arg(query, key):
    args = query.get(key, [])
    if args: return args[0]
    else: return None

def inspect_handler(path, post, query, *args):
    if path.startswith('/inspect'):
      return '<li>path: %s</li>\n<li>post: %s</li>\n<li>query: %s</li>'%(path, post, repr(query))

def make_simple_wsgi_app(handler):
  def simple_handler(path, post, query):
      ret = handler(path, post, query)
      if ret: return 'text/html', handler(path, post, query)
  def simple_app(path, post, query):
      post = first_arg(query, 'post') or post
      handlers = [simple_handler, index_handler, dir_handler, file_handler, err_handler]
      mime, content = try_these(handlers, path, post, query)
      return ('200 OK', [('Content-Type', mime)]), content
  return make_wsgi_app(simple_app)

def make_wsgi_app(app):
    def wsgi_app(env, response):
        size = int(env.get('CONTENT_LENGTH') or '0')
        header, content = app(env.get('PATH_INFO'), env['wsgi.input'].read(size), parse_qs(env['QUERY_STRING']))
        response(*header)
        return content.encode('utf-8', 'ignore')
    return wsgi_app
            
def make_wsgi_server(app, port=8000):
    from wsgiref.simple_server import make_server
    return make_server('', port, app)

def run_wsgi_app(app, argv):
    if not argv:
        import cgitb; cgitb.enable()
        wsgiref.handlers.CGIHandler().run(app)
    else:
        port= int(argv[0])
        print "listening on port: ", port
        make_wsgi_server(app, port).serve_forever()
  
if __name__ == '__main__':
  run_wsgi_app(make_simple_wsgi_app(inspect_handler), sys.argv[1:])
        
