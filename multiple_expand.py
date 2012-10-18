#!/usr/bin/env python2

import re
import itertools

def list_merge(ls):
    return reduce(lambda a,b: list(a)+list(b), ls, [])

printable_chrs = map(chr, range(32, 127))
def gen_range(start, end):
    if type(start) != str or type(end) != str or len(start) != len(end):
        raise Exception('not valid range:[%s,%s]'%(start, end))
    def get_pat(c):
        pat_list = ['[0-9]', '[a-z]', '[A-Z]', '.']
        return filter(lambda pat: re.match(pat, c), pat_list)[0]
    pat = ''.join(map(get_pat, start))
    candinates = [''.join(candicate) for candicate in itertools.product(* [printable_chrs] * len(start))]
    return filter(lambda x: re.match(pat, x) and x >= start and x <= end, candinates)
        
def parse_range(spec):
    m = re.match(r'\[(.+)\]', spec)
    if not m: return [spec]
    def _gen_range(r):
        if re.match('[+-]', r): _type, r = r[0], r[1:]
        else: _type = '+'
        m = re.match('(\w+)-(\w+)', r)
        return m and (_type, gen_range(*m.groups())) or (_type, [r])
    ranges = [_gen_range(r) for r in m.group(1).split(',')]
    included = [r for t, r in ranges if t == '+']
    excluded = [r for t, r in ranges if t == '-']
    included, excluded = list_merge(included), list_merge(excluded)
    return sorted(list(set(included) - set(excluded)))

def multiple_expand(str):
    '''>>> multiple_expand('ab[01-03,-02]cd[ab-ad,kl]')
['ab01cdab', 'ab01cdac', 'ab01cdad', 'ab01cdkl', 'ab03cdab', 'ab03cdac', 'ab03cdad', 'ab03cdkl']
'''
    return [''.join(parts) for parts in itertools.product(*[parse_range(i) for i in re.split('(\[.*?\])', str)])]

if __name__ == '__main__':
    print multiple_expand('ab[01-03,-02]cd[ab-ad,kl]')
