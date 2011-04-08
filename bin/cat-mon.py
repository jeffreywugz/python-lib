#!/usr/bin/python2
'''
cat-mon.py file
'''

import sys
import os.path
import time
import threading

if len(sys.argv) != 2:
    sys.stderr.write(__doc__)

def make_progress_reporter(total, get_counter):
    start = time.time()
    def report():
        counter = get_counter()
        used = time.time()-start
        percent = 1.0*(counter+1)/total
        sys.stderr.write("completed: %f%% used: %fs, remain: %fs\n" %(percent*100, used, used/percent - used))
    return report

def interval_times(interval):
    while True:
        yield time.time()
        time.sleep(interval)
        
size = os.path.getsize(sys.argv[1])
with open(sys.argv[1]) as f:
    report = make_progress_reporter(size, lambda :f.tell())
    t = threading.Thread(target=lambda :[report() for t in interval_times(5)])
    t.setDaemon(True)
    t.start()
    while f:
        sys.stdout.write(f.read(1024))
        sys.stdout.flush()
