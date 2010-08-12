#!/usr/bin/python
from common import *

class Attr(object):
    def __init__(self, d={}, **kw):
        self.dict = dict(d, **kw)

    def _parse(self, k, v):
        if k.startswith('%'):
            return str2dict(k[1:], v)
        return {}
        
    def parse(self, k, v):
        self.dict.update(self._parse(k,v))

    def set(self, k, v):
        self.dict.update({k:v})
        self.parse(k, v)
        
    def sub(self, v):
        return msub(v, self.dict)
    
    def get(self, k):
        return self.sub(self.dict[k])

    def __getattr__(self, k):
        return self.get(k)

    def __getitem__(self, k):
        return self.get(k)

    def __setitem__(self, k, v):
        return self.set(k, v)

    def __repr__(self):
        return 'Attr(%s)'%repr(self.dict)

    def __str__(self):
        return repr(self)

