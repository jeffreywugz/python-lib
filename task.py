from msite import *
from extra import *

def test_vgen():
    numbers = VisualDictSet(x=range(10), y=range(10))
    items = [('root','/'), ('home', '/ans42'), ('work', '/share/work')]
    def product(x,y, **kw): return x*y
    numbers.update(product=lambda x,y: x*y)
    print numbers.list_view('x', 'y', 'product')
    print numbers.table_view(target=product, row='x', col='y')
    print numbers.table_view(target='product', row='x', col='y')
    print core_templates.render('Aggregation.html',items=items)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()
    
