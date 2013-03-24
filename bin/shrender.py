#!/bin/env python2
'''
Execute cmd line by line
Usages:
echo date |./shrender.py text|qtext|web timeout
'''
import sys
import re
import copy
import traceback
from threading import Thread
from subprocess import Popen,PIPE,STDOUT

def pinfo(msg):
    print '\033[32m#%s\033[0m' %(msg)
def perror(msg):
    print '\033[31m%s\033[0m' %(msg)

def wait_child(p, timeout=-1):
    if timeout < 0: return p.wait()
    start_time = time.time()
    while p.returncode == None and time.time() < start_time + timeout:
        p.poll()
        time.sleep(0.01)
    else:
        try:
            p.terminate()
        except OSError, e:
            pass
        return -1
    return p.returncode

def popen(cmd, cwd=None, timeout=-1):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=cwd)
    output = p.communicate()[0]
    err = wait_child(p, timeout)
    if err:
        output = 'CmdError: dir=%s %s'%(cwd, cmd) + output
    return output

def sh(cmd, cwd=None, timeout=-1):
    p = Popen(cmd, shell=True)
    err = wait_child(p, timeout)
    return err

class Thread2(Thread):
    def __init__(self, func, *args, **kw):
        self.result = None
        def call_and_set(*args, **kw):
            self.result = func(*args, **kw)
        Thread.__init__(self, target=call_and_set, *args, **kw)
        self.setDaemon(True)

    def get(self, timeout=None):
        self.join(timeout)
        #return self.isAlive() and self.result
        return self.result

def make_async_func(f):
    def async_func(*args, **kw):
        t = Thread2(f, args=args, kwargs=kw)
        t.start()
        return t
    return async_func

def async_map(f, seq):
    return map(make_async_func(f), seq)

def async_get(seq, timeout):
    return map(lambda i: i.get(timeout), seq)

def find_attr(env, key):
    return eval(key, env, globals())

def sub(_str, env, find_attr=find_attr):
    '''>>> sub('$ab $$cd ${ef} $gh ${ij} $gh.i ${ij.i} $kl.i ${kl.i}', dict(gh=1, ij=2, kl=dict(i=3)))
'$ab $cd ${ef} 1 2 1.i ${ij.i} $kl.i 3'
>>> sub('${{a=2}} a=$a', {})
' a=2'
'''
    new_env = copy.copy(env)
    def handle_repl(m):
        def remove_brace(x):
            return re.sub('^{(.*)}$', r'\1', x or '')
        if m.group(1):
            expr = m.group(1)
            try:
                exec expr in globals(), new_env
            except Exception, e:
                print e, traceback.format_exc()
            return ''
        else:
            origon_expr = m.group(2) or m.group(3)
            expr = remove_brace(origon_expr)
            try:
                value = find_attr(new_env, expr)
                if type(value) == int or type(value) == float:
                    return '%.5g'%(value)
                if value == None or type(value) != str and type(value) != int and type(value) != float:
                    return '$%s'%(origon_expr)
                return str(value)
            except Exception, e:
                print 'WARN: sub():', e, 'when sub:', origon_expr
                print traceback.format_exc()
                #return 'X'
                return '$%s'%(origon_expr)
                #raise Fail('no sub', origon_expr)
    return re.sub('(?s)(?<![$])\${{(.+?)}}|\$(\w+)|\$({.+?})', handle_repl, _str).replace('$$', '$')

def li(format='%s', sep=' '):
    return lambda seq: sep.join([format% i for i in seq])

def add_html_style(row):
    def get_html_style(cell):
        if not cell: return 'color:red;'
        return "CmdError" in cell and 'color:red;' or 'color:black;'
    return [(get_html_style(cell), cell) for cell in row]

def render_table(table):
    tpl = """<div><table border="1">
  ${li('<tr>%s</tr>')([li('<th>%s</th>')(row) for row in data[:1]])}
  ${li('<tr>%s</tr>')([li('<td style="%s;text-align:left;"><pre>%s</pre></td>')(add_html_style(row)) for row in data[1:]])}
  </table></div>"""
    return sub(tpl, dict(data=table))

def do_cmd(term, cmd_list, timeout=1):
    if not cmd_list: return
    if term == 'echo':
        for cmd in cmd_list:
            print cmd
    elif term == 'text':
        return map(lambda cmd: pinfo(cmd) or (cmd, sh(cmd)), cmd_list)
    elif term == 'qtext':
        result = async_get(async_map(lambda cmd: popen(cmd), cmd_list), timeout)
        result = zip(cmd_list, result)
        for cmd, output in result:
            pinfo(cmd)
            if type(output) == str and 'CmdError' not in output:
                print output.strip()
            else:
                perror(output)
    elif term == 'html':
        result = async_get(async_map(lambda cmd: popen(cmd), cmd_list), timeout)
        result = zip(cmd_list, result)
        print render_table(["CMD output".split()] + result)
    else:
        return 'Not Support Term[%s]: %s'%(term, cmd_list)
    
if __name__ == '__main__':
    term = len(sys.argv) >= 2 and sys.argv[1] or "help"
    timeout = len(sys.argv) >= 3 and int(sys.argv[2]) or 1
    if term == 'help':
        print __doc__
        sys.exit(1)
    ret = do_cmd(term, [line.strip() for line in sys.stdin.readlines()], timeout)
    #print ret
