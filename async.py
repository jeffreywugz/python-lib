#!/usr/bin/env python2
from threading import Thread
import time

class Thread2(Thread):
    def __init__(self, func, *args, **kw):
        self.result = None
        def call_and_set(*args, **kw):
            self.result = func(*args, **kw)
        Thread.__init__(self, target=call_and_set, *args, **kw)

    def get(self, timeout=None):
        self.join(timeout)
        #return self.isAlive() and self.result
        return self.result

def make_async_func(f):
    def async_func(*args, **kw):
        t = Thread2(f, args=args, kwargs=kw)
        t.start()
        return t
    return async_func

def async_map(f, seq):
    return map(make_async_func(f), seq)

def async_get(seq, timeout):
    return map(lambda i: i.get(timeout), seq)

if __name__ == '__main__':
    print async_get(async_map(lambda i: time.sleep(i) or i, range(3)), 4)
