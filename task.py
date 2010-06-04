from msite import *
from extra import *

def test_vgen():
    numbers = VisualDictSet(x=range(10), y=range(10))
    items = [('root','/'), ('home', '/ans42'), ('work', '/share/work')]
    def product(x,y): return x*y
    print numbers.list_view('x', 'y', product=product)
    print numbers.table_view(target=product, row='x', col='y')
    print vgen.render_aggregation(items)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()
    
