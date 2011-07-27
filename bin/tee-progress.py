#!/usr/bin/env python2
'''
tee-progress.py ref-file
'''

import sys
import os.path
import time
import threading

if len(sys.argv) != 2:
    print sys.argv
    sys.stderr.write(__doc__)
    sys.exit(-1)

def make_progress_reporter(total, get_counter):
    start = time.time()
    def report():
        counter = get_counter()
        used = time.time()-start
        percent = 1.0*(counter+1)/total
        sys.stderr.write("completed: %d/%d=%f%% used: %fs, remain: %fs\n" %(counter, total, percent*100, used, used/percent - used))
    return report

def interval_times(interval):
    while True:
        yield time.time()
        time.sleep(interval)

with open(sys.argv[1]) as f:
    total = len(f.readlines())
    
def get_counter():
    return get_counter.counter
get_counter.counter = 0

report = make_progress_reporter(total, get_counter)
t = threading.Thread(target=lambda :[report() for t in interval_times(5)])
t.setDaemon(True)
t.start()
for k,line in enumerate(sys.stdin):
    sys.stdout.write(line)
    get_counter.counter = k
