#!/usr/bin/python2
import sys
import re
import numpy as np
import matplotlib.pyplot as plt

def radar_xticks(xticks):
    plt.xticks(np.arange(0, 2*np.pi, 2*np.pi/len(xticks)), xticks)

def radar(x, **kw):
    thetas = np.concatenate((np.arange(0, 2*np.pi, 2*np.pi/len(x)), [2*np.pi]))
    plt.polar(thetas, np.concatenate((x, x[0:1])), **kw)
    plt.fill(thetas, np.concatenate((x, x[0:1])), alpha=0.25)
    
def radars(group_names, attr_names, *xs, **kw):
    for label, x in zip(group_names, xs):
        radar(x, label=label)
    radar_xticks(attr_names)
    plt.legend()

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

def load_2d(path):
    header, data = table_load(path)
    data = transpose(data)
    col_names = header[1:]
    row_names, columned_data =  data[0], data[1:]
    columned_data = [map(float, col) for col in columned_data]
    return row_names, col_names, columned_data
    
def plt_dump(file):
    if not file or file.endswith('.plot'): plt.show()
    else: plt.savefig(file)

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print './%s data-file img-file' % sys.argv[1]
        sys.exit()
    row_names, col_names, columned_data = load_2d(sys.argv[1])
    radars(row_names, col_names, *np.transpose(columned_data))
    # plt.xticks(range(len(groups)), groups, rotation=90)
    plt_dump(sys.argv[2])
