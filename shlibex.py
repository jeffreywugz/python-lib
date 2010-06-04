import os, os.path
from glob import glob

def mkdir(dir):
    if not os.path.exists(dir): os.mkdir(dir)

def files(*arg):
    return list_([glob(item) for item in list_(arg)])
