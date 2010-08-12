#!/usr/bin/python
import sys
import os, os.path
import exceptions
import re
import time

class Store:
    def __init__(self, path, default_value=None):
        self.path, self.default_value = path, default_value

    def set(self, value):
        f = open(self.path, 'w')
        f.write(repr(value))
        f.close()

    def get(self):
        try:
            f = open(self.path)
            value = eval(f.read())
            f.close()
            return value
        except exceptions.IOError:
            return self.default_value

class Log:
    def __init__(self, path):
        self.path = path

    def record(self, *fields):
        list = [time.time()]
        list.extend(fields)
        f = open(self.path, 'a')
        f.write(repr(list)+'\n')
        f.close()

    def get(self):
        def safe_eval(x):
            try:
                return eval(x)
            except exceptions.Exception:
                return None
        f = open(self.path)
        lines = f.readlines()
        f.close()
        values = [safe_eval(line) for line in lines]
        return filter(None, values)
    
class HostInfoException(exceptions.Exception):
    def __init__(self, msg, obj=None):
        exceptions.Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "Get Host Info Exception: %s\n%s"%(self.msg, self.obj)

def mkdir(dir):
    if not os.path.exists(dir): os.mkdir(dir)

def popen(cmd):
    return os.popen(cmd).read()

def read(file):
    f = open(file)
    result = f.read()
    f.close()
    return result

def readlines(file):
    content = read(file)
    return filter(None, content.split('\n'))

def get_hostname():
    return popen('hostname').strip()

def get_arch_info():
    hostname = popen('uname -n').strip()
    arch = popen('uname -m').strip()
    cpu = popen('uname -p').strip()
    kernel = popen('uname -r').strip()
    return hostname, arch, cpu, kernel
    
def get_cpu_info():
    content = read('/proc/cpuinfo')
    n_cpu = len(re.findall('processor\t: ([0-9]+)\n', content))
    cpu_mhz = float(re.search('cpu MHz\t\t: ([.0-9]+)', content).group(1))
    cache_size = int(re.search('cache size\t: ([0-9])+ KB', content).group(1))
    cpu_model = re.search('model name\t: (.+?)\n', content).group(1)
    return n_cpu, cpu_mhz, cache_size, cpu_model

def get_mem_info():
    total, used = get_mem_stat()
    return total

def get_cpu_stat():
    user_mode, user_low, sys_mode, idle = readlines('/proc/stat')[0].split()[1:5]
    busy, idle = int(user_mode) + int(user_low) + int(sys_mode), int(idle)
    return busy, idle
    
def get_mem_stat():
    meminfo_list = [re.split('[: ]+', i)[1] for i in readlines('/proc/meminfo')]
    total_mem, used_mem = int(meminfo_list[0]), int(meminfo_list[1])
    return total_mem, used_mem
    
def get_disk_stat():
    content = popen('vmstat -D')
    pattern = """
 +([0-9]+) merged reads
 +([0-9]+) read sectors
.*
 +([0-9]+) merged writes
 +([0-9]+) written sectors
"""
    match = re.search(pattern, content, re.S)
    merged_reads, read_sectors, merged_writes, written_sectors = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return merged_reads, read_sectors, merged_writes, written_sectors

def get_net_stat():
    content = popen('netstat -s')
    pattern = """Ip:
.*
 +([0-9]+) incoming packets delivered
 +([0-9]+) requests sent out
.*
Tcp:
 +([0-9]+) active connections openings
 +([0-9]+) passive connection openings
"""
    match = re.search(pattern, content, re.S)
    in_pkts, out_pkts, active_conn, passive_conn = int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return in_pkts, out_pkts, active_conn, passive_conn

def slide2(func, seq):
    last, cur = seq[:-1], seq[1:]
    return map(func, last, cur)

def slice_seq_by_interval(seq, interval):
    return [seq[i] for i in range(0, len(seq), interval)]

def fold_seq_by_interval(seq, interval):
    return slide2(lambda i0,i1: seq[i0:i1], range(0, len(seq), interval))

def interval_slide2(func, seq, interval):
    return slide2(func, slice_seq_by_interval(seq, interval))

def transpose(matrix):
    cols = [[] for i in matrix[0]] # Note: You can not write cols = [[]] * len(matrix[0]); if so, all col in cols will ref to same list object 
    for row in matrix:
        map(lambda col,i: col.append(i), cols, row)
    return cols

def make_slicer(i):
    def slicer(*seq):
        return seq[i]
    return slicer

def log_diff(i0, i1):
    interval = i1[0] - i0[0]
    diff = map(lambda x0,x1: 1.0*(x1-x0)/interval, i0, i1)
    diff[0] = i1[0]
    return diff

def log_int(seq):
    cols = transpose(seq)
    t, values = cols[0], cols[1:]
    interval = t[-1] - t[0]
    values = map(lambda i: 1.0*sum(i)/interval, values)
    return [t[-1]] + values

def time_series_diff(seq, interval):
    return interval_slide2(log_diff, seq, interval)

def time_series_int(seq, interval):
    series = fold_seq_by_interval(seq, interval)
    return map(log_int, series)
    
def make_time_series_diff_extractor(getter, extractor):
    def series_diff_extractor(interval):
        series = time_series_diff(getter(), interval)
        return [(i[0], extractor(*i[1:])) for i in series]
    return series_diff_extractor

def make_time_series_int_extractor(getter, extractor):
    def series_int_extractor(interval):
        series = time_series_int(getter(), interval)
        return [(i[0], extractor(*i[1:])) for i in series]
    return series_int_extractor

class HMon:
    def __init__(self, log_dir='log', hostname=None):
        self.log_dir = log_dir
        mkdir(log_dir)
        if not hostname: self.hostname = get_hostname()
        else: self.hostname = hostname
        self.static_info = Store(self.gen_file_name('static'))
        self.cpu_log = Log(self.gen_file_name('cpu'))
        self.mem_log = Log(self.gen_file_name('mem'))
        self.disk_log = Log(self.gen_file_name('disk'))
        self.net_log = Log(self.gen_file_name('net'))
        self.get_cpu_usages = make_time_series_diff_extractor(self.get_cpu_history, lambda busy,idle: 1.0*busy/(idle+busy))
        self.get_mem_usages = make_time_series_int_extractor(self.get_mem_history, lambda total,usage: 1.0*usage/total)
        self.get_disk_read_amounts = make_time_series_diff_extractor(self.get_disk_history, make_slicer(1))
        self.get_disk_write_amounts = make_time_series_diff_extractor(self.get_disk_history, make_slicer(3))
        self.get_net_in_pkts = make_time_series_diff_extractor(self.get_net_history, make_slicer(0))
        self.get_net_out_pkts = make_time_series_diff_extractor(self.get_net_history, make_slicer(1))

    def gen_file_name(self, type):
        return os.path.join(self.log_dir, '%s.%s'%(type, self.hostname))
    
    def record_static_info(self):
        self.static_info.set(dict(arch=get_arch_info(), cpu=get_cpu_info(), mem=get_mem_info()))
        
    def get_static_info(self):
        return self.static_info.get()

    def record_dynamic_info(self):
        self.cpu_log.record(*get_cpu_stat())
        self.mem_log.record(*get_mem_stat())
        self.disk_log.record(*get_disk_stat())
        self.net_log.record(*get_net_stat())

    def recording_loop(self):
        while True:
            time.sleep(1)
            self.record_dynamic_info()

    def get_cpu_history(self):
        return self.cpu_log.get()

    def get_mem_history(self):
        return self.mem_log.get()

    def get_disk_history(self):
        return self.disk_log.get()

    def get_net_history(self):
        return self.net_log.get()
    
    def __str__(self):
        return "hostname:%s\nstatic info:\n%s"%(self.hostname, str(self.get()))

def main(log_dir):
    hmon = HMon(log_dir)
    print "record_static_info"
    try:
        hmon.record_static_info()
    except exceptions.IOError:
        print "record static info failed!"
    print "record_dynamic_info..."
    sys.stdout.flush()
    sys.stderr.flush()
    hmon.recording_loop()

if __name__ == '__main__':
    main(sys.argv[1])
