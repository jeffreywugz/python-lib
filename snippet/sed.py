def update_file(name, content):
    def need_update(name, content):
        if not os.path.exists(name):
            return True
        return open(name).read() != content
    if need_update(name, content):
        file = open(name, 'w')
        file.write(content)
        file.close()
        return True
    return False

class TagNotMatch(Exception):
    def __init__(self, begin, end):
        self.begin, self.end = begin, end

    def __str__(self):
        return 'Tag does not match: %s %s'%(self.begin, self.end)

class Sed:
    def __init__(self, comment='#'):
        self.comment = comment

    @staticmethod
    def _split(str, comment):
        sep1 = '(^%s\s*@\w+.*?\s*\n)' %(comment)
        sep2 = '(^%s\s*!<(?:\w+).*?^%s (?:\w+)>!\s*\n)' %(comment, comment)
        sep = '%s|%s'%(sep1, sep2)
        sep = re.compile(sep, re.M|re.S)
        return filter(None, re.split(sep, str))
        
    @staticmethod
    def _tag(str, comment):
        tag1 = '^%s\s*@(\w+)(.*)\s*\n' %(comment)
        tag2 = '^%s\s*!<(\w+)(.*)^%s (\w+)>!\s*\n'%(comment, comment)
        tag1 = re.compile(tag1)
        tag2 = re.compile(tag2, re.M|re.S)
        m1 = re.match(tag1, str)
        m2 = re.match(tag2, str)
        if m1:
            tag, content = m1.groups()
            return tag, content
        elif m2:
            begin_tag, content, end_tag = m2.groups()
            if begin_tag != end_tag:
                raise TagNotMatch(begin_tag, end_tag)
            return begin_tag, content
        else:
            return 'normal', str
    
    def gen_chunk(self, str):
        return '%s !<gen\n%s\n%s gen>!\n' %(self.comment, str, self.comment)
    
    def _chunk(self, str):
        chunks = self._split(str, self.comment)
        return [self._tag(str, self.comment) + (str,) for str in chunks]

    def sed(self, str):
        chunk_list = self._chunk(str)
        new_chunk_list = [getattr(self, tag)(content, raw) for tag, content, raw in chunk_list]
        return ''.join(new_chunk_list)

    def update(self, file_name):
        new_file = self.sed(open(file_name).read())
        return update_file(file_name, new_file)
        
    def normal(self, content, raw):
        return raw

    def gen(self, content, raw):
        return ''
