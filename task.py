from msite import *
from extra import *

def test_control():
    numbers = VisualDictSet(x=range(10), y=range(10))
    def product(x,y, **kw): return x*y
    numbers.update(product=lambda x,y: x*y)
    print numbers.list_view('x', 'y', 'product')
    print numbers.table_view(target=product, row='x', col='y')
    print numbers.table_view(target='product', row='x', col='y')

def test_container():
    views = [('home', '/ans42'), ('work', '/share/work')]
    print core_templates.render('panels.html',views=views)
    print core_templates.render('tabs.html', views=views)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()

wiki = Wiki('.')
