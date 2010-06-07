import os, os.path
from glob import glob


def files(*arg):
    return list_([glob(item) for item in list_(arg)])
