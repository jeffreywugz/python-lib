#!/bin/env python2
# -*- coding: utf-8 -*-

'''
  ./ob-review.py sample.post-review  --ignore=obfarm -r review_id
##### sample.post-review content #####################
* summary
  [1.0dev newfeature] 新增xxx
* desc
  新增功能
* test
  全覆盖
* file_list
  src/clog/ob_xxx.{h,cpp} unittest/clog/test_xxx.cpp
* review_id
  xxx
######################################################
'''
import sys
import re
import string
from subprocess import Popen

def sh(cmd='',  dir='.'):
    return cmd
    return Popen(cmd,  cwd=dir, shell=True).wait()
    
def sub(tpl, attrs):
    return string.Template(tpl).substitute(attrs)

def safe_read(path):
    with open(path) as f:
        return f.read()

def write(path, content):
    with open(path, "w") as f:
        f.write(content)

def parse_section(content):
    return dict((k, v.strip()) for k, v in re.findall("^[*] (.+?)\n(.+?)(?=^[*])", content, re.M|re.S))

def prepare_review_msg_file(file, attrs):
    review_msg = '''* 描述信息\n  $desc\n* 单元测试情况\n  $test\n'''
    write(file, sub(review_msg, attrs))

def prepare_review_cmd(attrs, extra_args):
    review_msg_file = "./review.msg"
    cmd = '''./ob-review --summary="$summary" --description-file=$review_msg_file --target-groups=oceanbase --target-people=yanran.hfs,yubai.lk,wenliang.zwl --server=http://rb.corp.taobao.com  $file_list $extra_args'''
    attrs.update(review_msg_file=review_msg_file, extra_args=' '.join(extra_args))
    prepare_review_msg_file(review_msg_file, attrs)
    return sub(cmd, attrs)

def help():
    sys.stderr.write(__doc__)

if __name__ == '__main__':
    len(sys.argv) >= 2 or help() or sys.exit(1)
    path, extra_args = sys.argv[1], sys.argv[2:]
    try:
        content = safe_read(path)
    except IOError as e:
        print "file read error:", e
        sys.exit(1)
    file_attrs = parse_section(content + '\n*')
    cmd = prepare_review_cmd(file_attrs, extra_args)
    print sh(cmd)
