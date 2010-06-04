from common import *
import vgen

class VisualDictSet(DictSet):
    def __init__(self, *args, **kw):
        DictSet.__init__(self, *args, **kw)

    def enum_attr_values(self, attr):
        attr_values = self.map(lambda **d: d.get(attr, None))
        attr_values = filter(lambda x: x != None, attr_values)
        return sorted(list(set(attr_values)))
        
    def list_view(self, *cols, **kw):
        self.update(**kw)
        full_cols = cols + tuple(kw.keys())
        print vgen.render_list(self.dicts, *full_cols)

    def table_view(self, target, row, col):
        def select_target_field(row_value, col_value):
            result = self.query(**{col: col_value, row: row_value})
            if len(result) == 1: return result[0]
            return result
        
        if callable(target): cell_maker = target
        else: cell_maker = select_target_field
        
        rows = self.enum_attr_values(row)
        cols = self.enum_attr_values(col)
        print vgen.render_table(cell_maker, rows, cols)
        

