#!/usr/bin/env python2

import sys
from wsgilib import make_simple_wsgi_app, run_wsgi_app
from smallseg import SEG

_seg = SEG()
def seg_handler(path, post, *args):
  print path, post
  if path == '/seg' and post:
    return '\n'.join(_seg.cut(post))

if __name__ == '__main__':
  run_wsgi_app(make_simple_wsgi_app(seg_handler), sys.argv[1:])
        
