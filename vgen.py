#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
import copy
import config
from mako.template import Template
from common import *

def is_image(name):
    return mos.get_ext(name) in ['png', 'gif', 'jpg']

def is_embed(name):
    return mos.get_ext(name) in ['svg', 'swf']
    
def file_view(name):
    if is_embed(name):
        return '<embed src="%s"/>'%(name)
    elif is_image(name):
        return '<img src="%s" alt="%s"/>'%(name, "image not found!")
    else:
        return mstore.safe_read(name)

def render_list(objs, cols):
    list_template = os.path.join(cwd, 'List.html')
    return Template(filename=list_template, disable_unicode=True).render(data=objs, cols=cols)
    
def render_table(cell_maker, rows, cols):
    table_template = os.path.join(cwd, 'Table.html')
    return Template(filename=table_template, disable_unicode=True).render(cell_maker=cell_maker, rows=rows, cols=cols)

class MultiShell:
    def __init__(self, log_dir, console_file='console.$host', *profile_list):
        self.log_dir, self.profile_list, self.console_file = log_dir, profile_list, console_file
        self.profile = malgo.dcmap(malgo.dmerge, *profile_list)
        malgo.lset(self.profile, 'console_file', lambda env: mstr.sub('%s/%s'%(log_dir, console_file), **env))

    def run(self, cmd_pattern):
        mos.mkdir(self.log_dir)
        malgo.lset(self.profile, 'console_cmd', lambda env: mstr.msub('%s >$console_file 2>&1 &'%(cmd_pattern), **env))
        map(lambda x:mos.shell(x['console_cmd']), self.profile)
    
    def genview(self, output, col='host', row=None):
        malgo.lset(self.profile, 'console_content', lambda env: mstore.safe_read(env['console_file']))
        def get_console_file(objs):
            return reduce(lambda x,y: x+y, [i['console_content'] for i in objs], "")
        def cell_maker(row_value, col_value):
            if row == None:
                return get_console_file(malgo.lquery(self.profile, **{col: col_value}))
            else:
                return get_console_file(malgo.lquery(self.profile, **{col: col_value, row: row_value}))
        cols = sorted(list(set([i[col] for i in self.profile])))
        if row == None:
            rows = ['console']
        else:
            rows = sorted(list(set([i[row] for i in self.profile])))
        mstore.write(output, render_table(cell_maker, rows, cols))
