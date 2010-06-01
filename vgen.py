#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
from common import *
import shell
import algo
from mako.template import Template

def is_image(name):
    return shell.get_ext(name) in ['png', 'gif', 'jpg']

def is_embed(name):
    return shell.get_ext(name) in ['svg', 'swf']
    
def file_view(name):
    if is_embed(name):
        return '<embed src="%s"/>'%(name)
    elif is_image(name):
        return '<img src="%s" alt="%s"/>'%(name, "image not found!")
    else:
        return safe_read(name)

def render_list(objs, *cols):
    list_template = os.path.join(cwd, 'res', 'List.html')
    return Template(filename=list_template, disable_unicode=True).render(data=objs, cols=cols)
    
def render_table(cell_maker, rows, cols):
    table_template = os.path.join(cwd, 'res', 'Table.html')
    return Template(filename=table_template, disable_unicode=True).render(cell_maker=cell_maker, rows=rows, cols=cols)

if __name__ == '__main__':
    numbers = algo.dcmap(algo.dmerge, [dict(x=i) for i in range(10)], [dict(y=i) for i in range(10)])
    algo.lset(numbers, 'product', lambda env: env['x'] * env['y']) 
    print render_list(numbers, 'product', 'x', 'y')
    print render_table(lambda x,y: x*y, range(10), range(10))
