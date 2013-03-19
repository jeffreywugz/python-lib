#!/bin/env python2
'''
Expand to multiple lines
Usages:
 ./expand.py echo [[ {1..3} ]]
 ./expand.py ssh  [[ hostname{1,2,3} ]] [[ uptime date ]]
 ./expand.py ssh  ...ip-list.txt [[ uptime date ]]
'''
import sys
import re
from subprocess import Popen
try:
    from itertools import product
except Exception, e:
    def product(*iterables, **kwargs):
        if len(iterables) == 0:
            yield ()
        else:
            iterables = iterables * kwargs.get('repeat', 1)
            for item in iterables[0]:
                for items in product(*iterables[1:]):
                    yield (item, ) + items

def list_merge(ls):
    return reduce(lambda a,b: list(a)+list(b), ls, [])

def safe_read_lines(x):
    try:
        with open(x) as f:
            return filter(None, [line.strip() for line in f.readlines()])
    except IOError,e:
        print e
        return [x]

start_marker, end_marker = '[[', ']]'
def expand_file_lines(args):
    def load_file_lines_maybe(x):
        if x.startswith('...'):
            return [start_marker] + safe_read_lines(x[3:]) + [end_marker]
        else:
            return [x]
    return list_merge(map(load_file_lines_maybe, args))

def expand_markers(args):
    def split_marker_maybe(x):
        m = re.match('(\[\[)(.*)(\]\])', x)
        if m:
            if m.group(2).startswith('...'):
                return [m.group(2)]
            else:
                return m.groups()
        return [x]
    return list_merge(map(split_marker_maybe, args))

def cmd_iter(argv):
    last_stat, cur_list = '', []
    for x in argv:
        if last_stat == start_marker:
            if x == end_marker: last_stat = ''; yield cur_list
            else: cur_list.append(x)
        else:
            if x == start_marker:
                last_stat, cur_list = start_marker, []
            else:
                yield [x]
            
def expand_multi_cmd(argv):
    return product(*list(cmd_iter(expand_file_lines(expand_markers(argv)))))

def sh(argv, cwd=None, timeout=-1):
    return Popen(argv, cwd=cwd).wait()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    for cmd in expand_multi_cmd(sys.argv[1:]):
        print ' '.join(cmd)
