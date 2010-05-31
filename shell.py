def mkdir(dir):
    if not os.path.exists(dir): os.mkdir(dir)

def get_ext(name):
    index = name.rfind('.')
    if index == -1: return ""
    return name[index+1:].lower()

def files(*arg):
    return list_([glob(item) for item in list_(arg)])
