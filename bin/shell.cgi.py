#!/usr/bin/python

import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.join(cwd, '../lib/mako.zip')])
from mako.template import Template
import cgi
import cgitb
import subprocess
cgitb.enable()

args = cgi.FieldStorage()
cmd = args.getfirst('cmd', 'true')
workdir = os.path.realpath(args.getfirst('workdir', '.'))

expand_cmd="sudo -n -u ans42 bash -c 'export HOME=/home/ans42; . /home/ans42/.bashrc; %s'"%(cmd)
p = subprocess.Popen(expand_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workdir)
stdout = p.stdout.read()
stderr = p.stderr.read()
p.wait()
print Template(filename=os.path.join(cwd, '../res/shell.html'), disable_unicode=True).render(cmd=cmd, workdir=workdir, stderr=stderr, stdout=stdout)
