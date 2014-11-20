#!/bin/env python2
# -*- coding: utf-8 -*-

'''
  ./ob-review.py sample.post-review
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

def prepare_review_cmd(attrs):
    def build_review_id_opt(review_id):
        if review_id:
            return "-r %s"%(review_id)
        else:
            return ""
    review_msg_file = "./review.msg"
    review_msg = '''* 描述信息\n  $desc\n* 单元测试情况\n  $test\n'''
    cmd = '''./ob-review --summary="$summary" --description-file=$review_msg_file --target-groups=oceanbase --target-people=yanran.hfs,yubai.lk,wenliang.zwl --server=http://rb.corp.taobao.com  --ignore=obfarm $file_list $review_id_opt'''
    attrs.update(review_msg_file=review_msg_file, review_id_opt=build_review_id_opt(attrs.get("review_id", "")))
    write(review_msg_file, sub(review_msg, attrs))
    return sub(cmd, attrs)

def help():
    sys.stderr.write(__doc__)

if __name__ == '__main__':
    len(sys.argv) == 2 or help() or sys.exit(1)
    path = sys.argv[1]
    try:
        content = safe_read(path)
    except IOError as e:
        print "file read error:", e
        sys.exit(1)
    file_attrs = parse_section(content + '\n*')
    cmd = prepare_review_cmd(file_attrs)
    print sh(cmd)
