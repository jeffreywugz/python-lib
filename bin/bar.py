#!/usr/bin/env python2

import sys
import os
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['figure.figsize']=(8,6)
# plt.rcParams['figure.subplot.bottom']=0.15
# plt.rcParams['figure.subplot.left']=0.15
# plt.ticklabel_format(style='sci', scilimits=(-2,+3))

def plt_dump(file):
    if not file or file.endswith('.plot'): plt.show()
    else: plt.savefig(file)

def readlines(path):
    f = open(path)
    content = f.readlines()
    f.close()
    return filter(lambda x: not re.match('^\s*$', x), content)

def transpose(matrix):
    cols = [[] for i in matrix[0]] # Note: You can not write cols = [[]] * len(matrix[0]); if so, all col in cols will ref to same list object
    for row in matrix:
        map(lambda col,i: col.append(i), cols, row)
    return cols

def table_load(path):
    lines = [line.split() for line in readlines(path)]
    return lines[0], lines[1:]

def load_src(path):
    header, data = table_load(path)
    data = transpose(data)
    column_names = header[1:]
    group_names, column_data =  data[0], data[1:]
    column_data = [map(float, col) for col in column_data]
    return group_names, column_names, column_data

def get_path_id(path):
    return re.sub('^.*/', '', path).replace('.bar', '').replace('-', '_')

def normalize21(seq):
    s = sum(seq)
    return np.array(seq)/s

def identical(x):
    return x

def ypos_h(x):
    return [0 for i in x]

def ypos_v(x):
    return [0.0] + list(np.add.accumulate(x)[:-1])

def xpos_h(n, i):
    width = 0.6/n
    return width, 0.2 + width*i

def xpos_v(n, i):
    width = 0.4
    return 0.4, 0.3

configs = dict(
    workload_latency=dict(ylabel='Latency(s)'),
    workload_cpu=dict(ylabel='Cpu Usages'),
    workload_read=dict(ylabel='Read Sectors'),
    workload_cpi_inst=dict(ylabel='Cpi or Insts/1e9'),
    workload_cpi=dict(ylabel='CPI'),
    workload_inst=dict(ylabel='Instructions/s', ypos=ypos_v, xpos=xpos_v),
    workload_inst_mix0=dict(ylabel='Ratio', ypos=ypos_h, xpos=xpos_h),
    workload_stall=dict(ylabel='Normalized Stall Ratio', norm=normalize21, ypos=ypos_v, xpos=xpos_v),
    workload_mem_latency=dict(ylabel='Latency(cycles/s)', ypos=ypos_v, xpos=xpos_v),
    workload_mem_latency1=dict(ylabel='Latency(cycles/instruction)', ypos=ypos_v, xpos=xpos_v),
    workload_pgfault=dict(ylabel='PageFault', ypos=ypos_v, xpos=xpos_v),
    apps_inst_mix=dict(ylabel='Normalized Ratio', norm=normalize21, ypos=ypos_v, xpos=xpos_v),
    apps_inst_mix0=dict(ylabel='Origin Ratio', ypos=ypos_v, xpos=xpos_v),
    apps_cpi=dict(ylabel='CPI'),
    apps_stall=dict(ylabel='Stall'),
    apps_pipeline_stall=dict(ylabel='Normalized Ratio', norm=normalize21, ypos=ypos_v, xpos=xpos_v),
    apps_mem_latency=dict(ylabel='Normalized Latency', norm=normalize21, ypos=ypos_v, xpos=xpos_v),
    apps_mem_latency0=dict(ylabel='Latency', ypos=ypos_v, xpos=xpos_v),
    tps=dict(ylabel='TPS'),
    )

def plt_bar(column_names, column_values, norm, xpos, ypos):
    column_values = np.transpose(map(norm, np.transpose(column_values)))
    ypos_values = np.transpose(map(ypos, np.transpose(column_values)))
    xpos_values = [xpos(len(column_names), i) for i in range(len(column_names))]
    xpos_values = [(width, np.arange(len(column_values[0]))+offset) for width,offset in xpos_values]
    #hatchs, colors = '/\\x+|*', 'bgrcmy'
    hatchs, colors = '/\\x+|*', 'wwwwwww'
    for name, col, (width,xoffset), yoffset, hatch, color in zip(column_names, column_values, xpos_values, ypos_values, hatchs, colors):
        print 'plot: ', name, col, xoffset, yoffset, hatch, color
        plt.bar(xoffset, col, width=width, bottom=yoffset, hatch=hatch, color=color, label=name)

def xbar(src, target):
    config = configs.get(get_path_id(src), {})
    print 'config: ', config
    group_names, column_names, column_values = load_src(src)
    plt.ylabel(config.get('ylabel', 'y'))
    plt_bar(column_names, column_values,
            config.get('norm', identical), config.get('xpos', xpos_h), config.get('ypos', ypos_h))
    plt.xticks(np.arange(len(group_names))+.5, group_names)
    if len(column_names) > 1:
        plt.legend(ncol=len(column_names),  loc='upper center', bbox_to_anchor=(0.5, 1.1))
    plt_dump(target)

if __name__ == '__main__':
    # func = globals().get(sys.argv[1])
    # func(*sys.argv[2:])
    xbar(*sys.argv[1:])
