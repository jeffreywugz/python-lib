import sys, os, os.path
my_lib_dir = os.path.dirname(os.path.abspath(__file__))
lib_paths = ['.']
sys.path.extend([os.path.join(my_lib_dir, path) for path in lib_paths])

from debug import *
from funclib import *
from strutil import *
from shlib import *
from store import *
from dictset import *
