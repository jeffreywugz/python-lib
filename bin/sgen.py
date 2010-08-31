#!/usr/bin/python

"""
Usage: sgen.py foo.txt ...
"""
import sys
import os, os.path
import exceptions
from common import *
import traceback
import string, re

class SGenException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

def update_file(name, content):
    def need_update(name, content):
        if not os.path.exists(name):
            return True
        return open(name).read() != content
    if need_update(name, content):
        file = open(name, 'w')
        file.write(content)
        file.close()
        return True
    return False

def common_prefix(a, b, max=4):
    for i in range(max, 0, -1):
        if a[:i] == b[:i]: return a[:i]
    return ''
    
def sed(content, env={}, **kw):
    """ Example:
- Single Line Mode:  
    # <<<self=range(5)>>>
    # ----begin----
    [0,1,2,3,4]
    # ----end----
- Multiple Line Mode:
    # <<<
    # self=range(5)
    # >>>
    # ----begin----
    [0,1,2,3,4]
    # ----end----
    """
    
    content = re.sub('(?m)^.*--begin--.*\n(.|\n)*?^.*--end--.*\n', '', content)
    segments = re.split('(?sm)(^[^\n]*<<<<.*?>>>>.*?\n)', content)
    env.update(**kw)
    def parse_seg(raw):
        pat = '^.+<<<<\n?((?:.|\n)*?)>>>>.*\n'
        match = re.match(pat, seg)
        if not match: return None
        code  = match.group(1)
        comment_prefix = common_prefix(raw, code)
        code = re.sub('^%s'%(comment_prefix), '', code)
        return code
    def evil(seg):
        code = parse_seg(seg)
        if code == None: return seg
        try:
            exec code in env
        except exceptions.Exception,e:
            raise SGenException('Code Exec exception', e) 
        generated = env.get('self', '')
        pat = '(?s)<<<<.*>>>>'
        begin = re.sub(pat, '--begin--', seg)
        end = re.sub(pat, '--end--', seg)
        return '%s%s%s\n%s'%(seg, begin, generated, end)
    return ''.join([evil(seg) for seg in segments])

def sgen(f, env={}, **kw):
    old = safe_read(f)
    new = sed(old, env, **kw)
    return update_file(f, new)
    
def main(args):
    [sgen(i) for i in args]
    
if __name__ == '__main__':
    main(sys.argv[1:])
