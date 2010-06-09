#!/bin/bash

echo 'Content-Type: text/html'
echo ''
file=`basename $0 .cgi`
if [ -L $0 ]; then
    binfile=`readlink $0`;
else
    binfile=$0;
fi
bindir=`dirname $binfile`
errorfile=/tmp/$file.cgi.error
rm -rf $errorfile 2>&1
$bindir/$file-cgi 2>$errorfile || (echo '<pre style="color:red">'; cat $errorfile; echo '</pre>')
