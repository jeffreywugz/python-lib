#!/usr/bin/python2

import sys
"""
vfiles means `view files'
Usage: vfiles.py file_list
 this cmd will generate a html snippet to display the `file_list' according to their types
 , and dump the html snippet to stdout
"""

def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except IOError as e:
        return repr(e)
    
def get_ext(name):
    return name[name.rfind('.')+1:]

def is_image(name):
    return get_ext(name) in ['png', 'gif', 'jpg']

def is_embed(name):
    return get_ext(name) in ['svg', 'swf']

def file_view(name):
    if is_embed(name):
        return '<embed src="%s"/>'%(name)
    elif is_image(name):
        return '<img src="%s" alt="%s"/>'%(name, "image not found!")
    else:
        return '<pre>%s</pre>'% safe_read(name)


def view_files(file_list):
    return ''.join(['<div><h2>%s</h2><div>%s</div></div>'%(f, file_view(f)) for f in file_list])

print view_files(sys.argv[1:])
