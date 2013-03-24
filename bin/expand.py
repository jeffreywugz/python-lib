#!/bin/env python2
'''
Expand to multiple lines
Usages:
 ./expand.py echo [[ {1..3} ]]
 ./expand.py ssh  [[ hostname{1,2,3} ]] [[ uptime date ]]
 ./expand.py rsync -av ~/.ssh  @ip-list.txt:
'''
import sys
import re
from subprocess import Popen
from itertools import product
# try:
#     from itertools import product
# except Exception, e:
#     def product(*iterables, **kwargs):
#         if len(iterables) == 0:
#             yield ()
#         else:
#             iterables = iterables * kwargs.get('repeat', 1)
#             for item in iterables[0]:
#                 for items in product(*iterables[1:]):
#                     yield (item, ) + items

def list_merge(ls):
    return reduce(lambda a,b: list(a)+list(b), ls, [])

start_marker, end_marker, file_prefix = '[[', ']]', '@'
def safe_read_lines(x):
    if not x.startswith(file_prefix):
        return [x]
    try:
        with open(x[len(file_prefix):]) as f:
            raw_lines = [line.strip() for line in f.readlines()]
            return [line for line in raw_lines if line and not line.startswith('##')]
    except IOError,e:
        #print e
        return [x]

def expand_file_lines(x):
    return map(lambda li: ''.join(li), product(*map(safe_read_lines, re.split('(@[_A-Za-z0-9.]+)', x))))

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
    def expand_list_file_lines(li):
        return list_merge(map(expand_file_lines, li))
    return product(*map(expand_list_file_lines, cmd_iter(argv)))

def sh(argv, cwd=None, timeout=-1):
    return Popen(argv, cwd=cwd).wait()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(1)
    #print list(expand_file_lines(sys.argv[1]))
    for cmd in expand_multi_cmd(sys.argv[1:]):
        print ' '.join(cmd)
