import exceptions

def gen_name(*parts):
    return '.'.join(parts)

def safe_read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except exceptions.IOError:
        return ''

def write(path, content):
    with open(path, 'w') as f:
        f.write(content)
    
def get_ext(name):
    index = name.rfind('.')
    if index == -1: return ""
    return name[index+1:].lower()
