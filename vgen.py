#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
from common import *
import funclib, shlib

templates = TemplateSet(os.path.join(cwd, 'res'))

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

def render(filename, **kw):
    return templates.render(filename, **kw)

def render_list(objs, *cols):
    return templates.render('List.html', data=objs, cols=cols)

def render_table(cell_maker, rows, cols):
    return templates.render('Table.html', cell_maker=cell_maker, rows=rows, cols=cols)

def render_aggregation(items):
    return templates.render('Aggregation.html', items=items)

