from common import *

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
        return self.get_store(args).read()

    def __setitem__(self, args, result):
        return self.get_store(args).write(result)
    
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

class SeqStore:
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
    
    def read(self):
        if not self.check(): return None
        with open(self.path) as f:
            lines = f.readlines()
            return [eval(i) for i in lines]

    def write(self, seq):
        with open(self.path, 'w') as f:
            f.writelines([repr(i) + '\n' for i in seq])
        self.write_meta('complete')
