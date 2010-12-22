from common import *
import exceptions
import pickle
import sqlite3

"""Example:
def square(x):
    print 'square(%d)'% x
    return x*x

cached_square = quick_make_cached_func(square)
cached_square(3)
cached_square(3)
"""

def quick_make_cached_func(func, path=None, key=lambda x:x):
    if path == None: path = '/tmp/' + func.__name__
    return make_cached_func(MapWrapper(FileStore(path, eval, repr)), key, func)
    
def cached_call(map_store, key, func, *args, **kw):
    k = key(*args, **kw)
    if not map_store.has_key(k):
        map_store[k] = func(*args, **kw)
    return map_store[k]

def make_cached_func(store, key, func):
    return lambda *args, **kw: cached_call(store, key, func, *args, **kw)

class JournaledStore:
    def __init__(self, path):
        self.path = path

    def read_meta(self):
        try:
            with open(self.path + '.meta') as f:
                return f.read()
        except exceptions.Exception as e:
            return ""

    def write_meta(self, content):
        with open(self.path + '.meta', 'w') as f:
            f.write(content)
    
    def check(self):
        return self.read_meta() == 'complete'
    
    def load(self):
        if not self.check(): return None
        result = self.do_load()
        return result
        
    def dump(self, value):
        if os.path.exists(self.path): os.unlink(self.path)
        self.write_meta('in progress')
        self.do_dump(value)
        self.write_meta('complete')

class FileStore(JournaledStore):
    def __init__(self, path, loads, dumps):
        self.path, self.loads, self.dumps = path, loads, dumps
        JournaledStore.__init__(self, path)

    def do_load(self):
        with open(self.path) as f:
            return self.loads(f.read())

    def do_dump(self, value):
        with open(self.path, 'w') as f:
            return f.write(self.dumps(value))

class MapWrapper:
    def __init__(self, store):
        self.store = store

    def get(self):
        return self.store.load() or {}
    
    def set(self, d):
        return self.store.dump(d)
    
    def has_key(self, key):
        return self.get().has_key(key)
    
    def __getitem__(self, key):
        return self.get()[key]

    def __setitem__(self, key, value):
        d = self.get()
        d[key] = value
        return self.set(d)
    
class DBStore(JournaledStore):
    def __init__(self, path):
        FileStore.__init__(self,path)

    @staticmethod
    def get_types(table):
        type_map = {None:'NULL', int:'INTEGER', float:'REAL', str:'TEXT', str:'TEXT'}
        seq = table[0]
        return [type_map[type(i)] for i in seq]

    def get_conn(self):
        conn = sqlite3.connect(self.path)
        conn.text_factory = str
        return conn
        
    def do_load(self):
        select_cmd = 'select * from main'
        with self.get_conn() as conn:
            return conn.execute(select_cmd)

    def do_dump(self, table):
        types = self.get_types(table)
        create_table_cmd = 'create table main(%s)'%(', '.join(['col%d %s'%(i, type) for (i, type) in enumerate(types)]))
        insert_cmd = "insert into main(%s) values (%s)"%(', '.join(['col%d'%i for i in range(len(types))]), ', '.join(['?']* len(types)))
        print(create_table_cmd, insert_cmd)
        with self.get_conn() as conn:
            conn.execute(create_table_cmd)
            conn.executemany(insert_cmd, table)

class DirMapStore:
    def __init__(self, dir, file_store_maker):
        self.dir, self.file_store_maker = dir, file_store_maker

    def get_store(self, name):
        return self.file_store_maker(os.path.join(self.dir, name))

    def has_key(self, key):
        return True
    
    def __getitem__(self, name, default=None):
        return self.get_store(name)

    def __setitem__(self, name, result):
        raise exceptions.KeyError('Not allowed')
