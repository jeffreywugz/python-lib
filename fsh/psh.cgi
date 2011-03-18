#!/bin/bash

# echo 'Content-Type: text/html'
# echo ''
file=`basename $0 .cgi`
if [ -L $0 ]; then
    binfile=`readlink $0`;
else
    binfile=$0;
fi
bindir=`dirname $binfile`
errfile=/tmp/$file.cgi.err
sudo -n -u ans42 rm -rf $errorfile 2>&1
sudo -E -n -u ans42 bash -c "export HOME=/home/ans42; . /home/ans42/.bashrc; $bindir/psh.py 2>$errfile" || \
    (echo 'Content-Type: text/html\n\n' '<pre style="color:red">'; cat $errfile; echo '</pre>')

