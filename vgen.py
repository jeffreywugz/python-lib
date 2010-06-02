#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
from common import *
import shlib, algo
from mako.template import Template

def is_image(name):
    return shlib.get_ext(name) in ['png', 'gif', 'jpg']

def is_embed(name):
    return shlib.get_ext(name) in ['svg', 'swf']
    
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
