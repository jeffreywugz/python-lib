import sys, os, os.path
my_lib_dir = os.path.dirname(os.path.abspath(__file__))
lib_paths = ['.', 'lib/mako.zip', 'lib/cherrypy.zip']
sys.path.extend([os.path.join(my_lib_dir, path) for path in lib_paths])

from core import *
from store import *
from funclib import *
from dictset import *
from shlib import *
