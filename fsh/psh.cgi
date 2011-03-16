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
errorfile=/tmp/$file.cgi.error
sudo -n -u ans42 rm -rf $errorfile 2>&1
sudo -E -n -u ans42 bash -c "export HOME=/home/ans42; . /home/ans42/.bashrc; $bindir/psh.py 2>$errorfile" || (echo '<pre style="color:red">'; cat $errorfile; echo '</pre>')

