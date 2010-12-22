#!/usr/bin/python2

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

file_types = [
    ['image', ('png', 'gif', 'jpg'), lambda name: '<img src="%s" alt="%s"/>'%(name, "image not found!")],
    ['embed', ('svg', 'swf'), lambda name: '<embed src="%s"/>'%(name)],
    ['csv', ('csv'), lambda name: '<table border="1">%s</table>' % '\n'.join(
            ['<tr>%s</tr>'% '\n'.join(['<td>%s</td>'%cell for cell in row.split(',')]) for row in safe_read(name).split('\n')])],
    ['text', ('txt'), lambda name: '<pre>%s</pre>'% safe_read(name)],
    ['html', ('html'), lambda name: safe_read(name)],
]

def file_render(name):
    for type_def, suffix, render in file_types:
        if get_ext(name) in suffix:
            return render(name)
    return "unknown file type!"

def view_files(*file_list):
    return ''.join(['<div><h2>%s</h2><div>%s</div></div>'%(f, file_render(f)) for f in file_list])

if __name__ == '__main__':
    import sys
    print view_files(*sys.argv[1:])
