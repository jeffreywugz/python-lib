#!/usr/bin/env python2
'''
# add '$' to the end of your txt file path to view it as file-shell
http://host/path-to-your-file$
# this page see help
http://host/.../xx$help.html
'''

import os, os.path
import sys
my_fsh_dir = os.path.dirname(os.path.abspath(__file__))
import re
import traceback
import exceptions
from cStringIO import StringIO
import subprocess
import mimetypes
from cgi import parse_qs
from urllib import quote
import wsgiref.handlers

txt_header = 'Content-type: text/plain\n'

class PshException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'PshException(%s, %s)'%(repr(self.msg), repr(self.obj))

def popen(path, cmd):
    p = subprocess.Popen(cmd, cwd=os.path.dirname(path), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise PshException('%s\n%s'%(err, out), cmd)
    return out

def get(path, *args):
    try:
        with open(path, 'r') as f:
            return f.read()
    except exceptions.Exception,e:
        print e
        return ''

def set(path, content):
    with open(path, 'w') as f:
        f.write(content)

def echo(path, arg):
    return arg

def psh(func, path, content):
    print 'func:%s, path=%s, content=%s'%(func, path, content)
    result, tb = None, None
    try:
        result = eval(func)(path, content)
    except exceptions.Exception,e:
        print e
        result, tb = e, '%s %s\n%s\n'%(func, path, content) + traceback.format_exc()
    return [result, tb]

def rpc_encode(result, tb):
    if tb: return 'Exception:\n%s' % (tb)
    else: return 'OK:\n%s' %(result)

def get_mime_type(path):
    return mimetypes.guess_type(path)[0] or 'text/plain'

def listdir(path):
    files = [(i,os.path.join(path, i)) for i in ['..']+sorted(os.listdir(path))]
    files = [(name, path, ['', '/'][os.path.isdir(path)]) for name, path in files]
    files = [(name+slash, path+slash) for name,path,slash in files]
    files = ['<li><a href="%s"><pre>%s</pre></a>'%(quote(path), name) for name, path in files]
    return '<style type="text/css">pre{margin-top:0; margin-bottom:0;} pre:hover{background-color: red;}</style><ul>%s</ul>' % '\n'.join(files)

def serve_file(path):
    content = get(path)
    if content: return get_mime_type(path), get(path)

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

def fsh_handler(path, post, query):
    match = re.match('^(.*)\$(.*)$', path)
    if not match: return None
    path, method = match.groups()
    print 'fsh_handler(path=%s, method=%s)'%(path, method)
    path = path or '/tmp/scrath'
    method = method or 'fsh.html'
    response =  serve_file(os.path.join(my_fsh_dir, method))
    if response: return response
    return 'text/plain', rpc_encode(*psh(method, path, post))

def first_arg(query, key):
    args = query.get(key, [])
    if args: return args[0]
    else: return None

def psh_cgi_handler(post, query):
    path = first_arg(query, 'path') or '/tmp/scrath'
    method = first_arg(query, 'method') or 'get'
    sys.stdout = output = StringIO()
    ret = psh(method, path, post)
    output.getvalue()
    sys.stdout = sys.__stdout__
    return 'text/plain', rpc_encode(*ret)

def psh_app(path, post, query):
    # print txt_header
    # print repr(path), repr(post), repr(query)
    post = query.get('post', post)
    if path:
        handlers = [fsh_handler, index_handler, dir_handler, file_handler, err_handler]
        mime, content = try_these(handlers, path, post, query)
    else:
        mime, content = psh_cgi_handler(post, query)
    return ('200 OK', [('Content-Type', mime)]), content

def make_wsgi_app(app):
    def wsgi_app(env, response):
        size = int(env.get('CONTENT_LENGTH') or '0')
        header, content = app(env.get('PATH_INFO'), env['wsgi.input'].read(size), parse_qs(env['QUERY_STRING']))
        response(*header)
        return content
    return wsgi_app

def make_wsgi_server(app, port=8000):
    from wsgiref.simple_server import make_server
    return make_server('', port, app)

if __name__ == '__main__':
    app = make_wsgi_app(psh_app)
    if len(sys.argv) == 1:
        import cgitb; cgitb.enable()
        wsgiref.handlers.CGIHandler().run(app)
    else:
        port= int(sys.argv[1])
        print "listening on port: ", port
        make_wsgi_server(app, port).serve_forever()
