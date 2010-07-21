from common import *
import cPickle
import sqlite3

def cachedMethod(func):
    def wrapper(self, *args):
        name = func.__name__
        if not hasattr(self, 'cache'): setattr(self, 'cache', {})
        if not self.cache.has_key(name): self.cache[name] = {}
        if self.cache[name].has_key(args):
            result = self.cache[name][args]
        else:
            result = func(self, *args)
            self.cache[name][args] = result
        return result
    return wrapper

class FileStoreCache:
    def __init__(self, prefix, store_class):
        self.prefix, self.store_class = prefix, store_class

    def gen_path(self, args):
        return self.prefix + '-'.join([str(i) for i in args])

    def get_store(self, args):
        return self.store_class(self.gen_path(args))
        
    def has_key(self, key):
        return self.get_store(key).check()
    
    def __getitem__(self, args):
        return self.get_store(args).load()

    def __setitem__(self, args, result):
        return self.get_store(args).dump(result)
    
class DirCache:
    def __init__(self, dir, store_class):
        self.dir, self.store_class = dir, store_class

    def get_store(self, name):
        return FileStoreCache(os.path.join(self.dir, name), self.store_class)

    def has_key(self, key):
        return True
    
    def __getitem__(self, name, default=None):
        return self.get_store(name)

    def __setitem__(self, name, result):
        raise exceptions.KeyError('Not allowed')
            

class Store:
    def __init__(self, path, default_value=None):
        self.path, self.default_value = path, default_value

    def set(self, value):
        with open(self.path, 'w') as f:
            f.write(repr(value))

    def get(self):
        try:
            with open(self.path) as f:
                value = eval(f.read())
        except exceptions.IOError:
            return self.default_value
        return value

class Log:
    def __init__(self, path):
        self.path = path
        self.file = open(path, 'a+', 1)

    def __del__(self):
        self.file.close()
        
    def clear(self):
        pass
    
    def record(self, *fields):
        list = [time.time()]
        list.extend(fields)
        self.file.write(repr(list)+'\n')

    def get(self):
        lines = self.file.readlines()
        values = [safe_eval(line) for line in lines]
        return filter(None, values)

class FileStore:
    def __init__(self, path):
        self.path = path

    def read_meta(self):
        try:
            with open(self.path + '.meta') as f:
                return f.read()
        except exceptions.Exception,e:
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
        self.do_dump(value)
        self.write_meta('complete')

class SeqStore(FileStore):
    def __init__(self, path):
        self.path = path

    def do_load(self):
        with open(self.path) as f:
            lines = f.readlines()
            return [eval(i) for i in lines]

    def do_dump(self, f, seq):
        with open(self.path, 'w') as f:
            f.writelines([repr(i) + '\n' for i in seq])

class PickleStore(FileStore):
    def __init__(self, path):
        FileStore.__init__(self, path)

    def do_load(self):
        with open(self.path) as f:
            return cPickle.load(f)

    def do_dump(self, f, value):
        with open(self.path, 'w') as f:
            return cPickle.dump(value, f)
    
class DBStore(FileStore):
    def __init__(self, path):
        FileStore.__init__(self,path)

    @staticmethod
    def get_types(table):
        type_map = {None:'NULL', int:'INTEGER', float:'REAL', str:'TEXT', unicode:'TEXT'}
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
        print create_table_cmd, insert_cmd
        with self.get_conn() as conn:
            conn.execute(create_table_cmd)
            conn.executemany(insert_cmd, table)

        

