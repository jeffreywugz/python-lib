#!/usr/bin/python2

import sys
from htmlentitydefs import codepoint2name

def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint), 
            lambda m: unichr(name2codepoint[m.group(1)]), s)

def escape(str):
    names = codepoint2name
    return reduce(lambda a,b: a+b, map(lambda x: names.has_key(ord(x)) and '&'+names[ord(x)] or x, str))

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

if __name__ == '__main__':
    print html_escape(sys.stdin.read())
