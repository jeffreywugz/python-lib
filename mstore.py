import exceptions

def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except exceptions.IOError:
        return ''

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
class Store:
    def __init__(self, path, default_value=None):
        self.path, self.default_value = path, default_value

    def set(self, value):
        f = open(self.path, 'w')
        f.write(repr(value))
        f.close()

    def get(self):
        try:
            f = open(self.path)
            value = eval(f.read())
            f.close()
        except exceptions.IOError:
            return self.default_value
        return value
        
class Log:
    def __init__(self, path):
        self.path = path
        self.file = open(path, 'a+', 1)

    def __del__(self):
        self.file.close()
        
    def record(self, *fields):
        list = [time.time()]
        list.extend(fields)
        self.file.write(repr(list)+'\n')

    def get(self):
        lines = self.file.readlines()
        def safe_eval(expr, default):
            try:
                return eval(expr)
            except exceptions.Exception:
                return default
        values = [safe_eval(line, None) for line in lines]
        return filter(None, values)
