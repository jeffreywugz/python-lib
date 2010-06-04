from common import *
import vgen

class VisualDictSet(DictSet):
    def __init__(self, *args, **kw):
        DictSet.__init__(self, *args, **kw)

    def enum_attr_values(self, attr):
        attr_values = self.map(lambda **d: d.get(attr, None))
        attr_values = filter(lambda x: x != None, attr_values)
        return sorted(list(set(attr_values)))
        
    def list_view(self, *cols):
        print vgen.render_list(self.dicts, *cols)

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
        print vgen.render_table(cell_maker, rows, cols)
        

