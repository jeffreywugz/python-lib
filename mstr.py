import string

def gen_name(base, host):
    return '%s.%s'%(base, host)

def sub(template, **vars):
    return string.Template(template).safe_substitute(**vars)

def msub(template, **env):
    old = ""
    cur = template
    while cur != old:
        old = cur
        cur = sub(cur, **env)
    return cur
