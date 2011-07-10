#!/usr/bin/python2
"""
./dot-filter.py in-file |dot -Tpng -o out.png
this filter will call `cpp' first, then replace `<pre>.*</pre>' blocks by as following example shows:
<pre>int main()
{
   function();
   return 0;
}
</pre>

===>

int main()<br align="left">
{<br align="left">
   function();<br align="left">
   return 0;<br align="left">
}<br align="left">

"""

import sys
import re
from subprocess import Popen, PIPE, STDOUT

def popen(cmd):
    return Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT).communicate()[0]

def cpp(path):
    return popen('cpp %s' % path)

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def html_escape2(text):
    return html_escape(html_escape(text))

def pre_filter(str):
    def escape(str):
        return re.match('^\s*: ', str) and re.sub('^(\s*):(.*)$', r'\1\2', str) or html_escape2(str)
    def pre_sub(str):
        return '<font face="monospace">%s</font>'% re.sub('^(.*?)$', lambda m: escape(m.group(1)) + '<br align="left"/>', str, flags=re.M)
    return re.sub('<pre>(.*?)</pre>', lambda m: pre_sub(port_sub(m.group(1))), str, flags=re.S)

def port_sub(str):
    return re.sub('^(\s*)(.*):(\w+)->\s*$', lambda m: r'%s: <table><tr><td port="%s">%s</td></tr></table>'%(m.group(1), m.group(3), html_escape2(m.group(2))), str, flags=re.M)

def call_filter(str):
    def call_escape(str):
        if re.match('^.*:(\w+)->\s*$', str):
            return re.sub('^(.*):(\w+)->\s*$', lambda m: r'<tr><td port="%s" align="left" border="1"><b>%s</b></td></tr>'%(html_escape2(m.group(2)), m.group(1)), str)
        else:
            return '<tr><td align="left">%s</td></tr>'%(html_escape2(str))
        return re.match('^\s*: ', str) and re.sub('^(\s*):(.*)$', r'\1\2', str) or html_escape2(str)
    def call_sub(str):
        return re.sub('^(.*?)$', lambda m: call_escape(m.group(1)), str, flags=re.M)
    return re.sub('<call>(.*?)</call>', lambda m: '<table border="0" bgcolor="lightgray">%s</table>'%(call_sub(m.group(1))), str, flags=re.S)
    
if __name__ == '__main__':
    print call_filter(cpp(sys.argv[1]))

                 

