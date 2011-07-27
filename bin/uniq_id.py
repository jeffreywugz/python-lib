#!/usr/bin/env python2

import sys

# all at once
# seq = sys.stdin.readlines()
# id_map = dict((v,i) for i,v in enumerate(set(seq)))
# for i in seq:
#     print id_map[i]

def make_id_generator():
    id_map = {}
    def gen_id(i):
        if not id_map.has_key(i):
            id_map[i] = len(id_map)
        return id_map[i]
    return gen_id

gen_id = make_id_generator()
for line in sys.stdin:
    print gen_id(line)
