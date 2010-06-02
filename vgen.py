#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
from common import *
import shlib, algo
from mako.template import Template

class View:
    def __init__(self):
        self.templates = TemplateSet(os.path.join(cwd, 'res'))

    @staticmethod
    def is_image(name):
        return shlib.get_ext(name) in ['png', 'gif', 'jpg']

    @staticmethod
    def is_embed(name):
        return shlib.get_ext(name) in ['svg', 'swf']

    @staticmethod
    def file_view(name):
        if is_embed(name):
            return '<embed src="%s"/>'%(name)
        elif is_image(name):
            return '<img src="%s" alt="%s"/>'%(name, "image not found!")
        else:
            return safe_read(name)

    def render(self, filename, **kw):
        return self.templates.render(filename, **kw)
        
    def render_list(self, objs, *cols):
        return self.render('List.html', data=objs, cols=cols)

    def render_table(self, cell_maker, rows, cols):
        return self.render('Table.html', cell_maker=cell_maker, rows=rows, cols=cols)

    def render_aggregation(self, items):
        return self.render('Aggregation.html', items=items)
