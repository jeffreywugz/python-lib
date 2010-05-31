class Templet:
    def __init__(self, str):
        self.str = str

    def sub(self, sep=' ', env={}, **kw):
        preprocessed = re.sub('\$(\w+)', '${\\1}', self.str)
        segments = re.split('(?s)(\${.+?})', preprocessed)
        env.update(**kw)
        def evil(seg):
            if not re.match('\$', seg):
                return seg
            exp = re.sub('(?s)^\${(.+?)}', '\\1', seg)
            result = eval(exp, globals(), env)
            return sep.join([str(item) for item in list_(result)])
        return ''.join([evil(seg) for seg in segments])

def sub(template, env={}, sep=' ', **kw):
    return Templet(template).sub(env=env, sep=sep, **kw)

