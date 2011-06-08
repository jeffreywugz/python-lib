#!/usr/bin/python2
#Initial idea from David Warde-Farley on the SciPy Cookbook
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import NullLocator
#from matplotlib.collections import RegularPolyCollection
#from matplotlib.colors import BoundaryNorm, ListedColormap

def hinton(W, maxWeight=None, ax=None):
    """
    Draws a Hinton diagram for visualizing a weight matrix.
    """
    if not ax:
        fig = plt.figure(figsize=(8,4.5))
        ax = fig.add_subplot(111)

    if not maxWeight:
        maxWeight = 2**np.ceil(np.log(np.abs(W).max())/np.log(2))

    ax.patch.set_facecolor('gray')
    ax.set_aspect('equal', 'box')
    ax.xaxis.set_major_locator(NullLocator())
    ax.yaxis.set_major_locator(NullLocator())

    for (x,y),w in np.ndenumerate(W):
        if w > 0: color = 'white'
        else:     color = 'black'
        size = np.sqrt(np.abs(w))
        rect = Rectangle([x - size / 2, y - size / 2], size, size,
            facecolor=color, edgecolor=color)
        ax.add_patch(rect)
    for x, cols in enumerate(W):
        rect = Rectangle([x-0.3, -np.sum(cols)-1], 0.6, np.sum(cols),
            facecolor='black', edgecolor='black')
        ax.add_patch(rect)
    bbox_props = dict(fc="white",ec="black")
    t = ax.text(-.8, -2, "Average\nCorrelation", ha="right", va="bottom", bbox=bbox_props)
    ax.autoscale_view()

    # Reverse the yaxis limits
    ax.set_ylim(*ax.get_ylim()[::-1])

## Potential way using polygon collections that just has an issue with
## easily getting the squares scaled by the data.

#    height,width = W.shape
#    x = np.arange(width)
#    y = np.arange(height)
#    X,Y = np.meshgrid(x, y)
#    xy = np.array([X.flatten(),Y.flatten()]).T
#    scaled_data = W.flatten() / maxWeight
#    cmap = ListedColormap(['black', 'white'])
#    norm = BoundaryNorm([-1., 0., 1.], cmap.N)

#    rect_col = RegularPolyCollection(4, rotation=np.pi/4,
#        sizes=np.abs(scaled_data) * 72 / ax.figure.get_dpi(), offsets=xy,
#        transOffset=ax.transData, norm=norm, cmap=cmap, edgecolor='none')
#    ax.add_collection(rect_col)
#    rect_col.set_array(scaled_data)
#    ax.autoscale_view()

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

def plt_dump(file):
    if not file or file.endswith('.plot'): plt.show()
    else: plt.savefig(file)
    
if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print './hinto.py data-file img-file'
        sys.exit()
    groups, columns, data = load_src(sys.argv[1])
    hinton(np.transpose(data))
    plt.xticks(range(len(groups)), groups, rotation=90)
    plt.yticks(range(len(columns)), columns)
    plt_dump(sys.argv[2])

