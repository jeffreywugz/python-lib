#!/bin/bash

echo 'Content-Type: text/html'
echo ''
binfile=`readlink $0`
bindir=`dirname $binfile`
errorfile=/tmp/shell.cgi.error
rm -rf $errorfile 2>&1
$bindir/shell.cgi.py 2>$errorfile || (echo '<pre style="color:red">'; cat $errorfile; echo '</pre>')
