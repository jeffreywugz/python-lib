from common import *

class VisualDictSet(DictSet):
    def __init__(self, *args, **kw):
        DictSet.__init__(self, *args, **kw)

    def enum_attr_values(self, attr):
        attr_values = self.map(lambda **d: d.get(attr, None))
        attr_values = filter(lambda x: x != None, attr_values)
        return sorted(list(set(attr_values)))
        
    def list_view(self, *cols):
        print core_templates.render('List.html', data=self.dicts, cols=cols)

    def make_cell_maker(self, row, col, func, multiple=False):
        def cell_maker(row_value, col_value):
            result = self.query(**{col: col_value, row: row_value})
            if multiple:
                return func(*result)
            else:
                if len(result) == 0: return None
                else: return func(**result[0])
        return cell_maker
        
    def table_view(self, target, row, col):
        def default_cell_maker(**kw):
            return kw[target]
        
        if callable(target): cell_maker = self.make_cell_maker(row, col, target)
        else: cell_maker = self.make_cell_maker(row, col, default_cell_maker)
        
        rows = self.enum_attr_values(row)
        cols = self.enum_attr_values(col)
        print core_templates.render('Table.html', cell_maker=cell_maker, rows=rows, cols=cols)
        

class MultiShell(VisualDictSet):
    def __init__(self, *args, **kw):
        VisualDictSet.__init__(self, *args, **kw)

    def sub(self, *cmd, **kw):
        dicts = self * kw
        return dicts.map(lambda **env: msub(' '.join(cmd), **env))
        
    def run(self, *cmd, **kw):
        map(shell, self.sub(*cmd, **kw))

    def vrun(self, row, col, *cmd, **kw):
        def cell_maker(**env):
            env = dmerge(env, kw)
            return safe_popen(msub(' '.join(cmd), **env))
        self.table_view(target=cell_maker, row=row, col=col)
