from msite import *

def test_vgen():
    numbers = DictSet(x=range(10), y=range(10))
    numbers.update(product = lambda x,y: x*y)
    items = [('root','/'), ('home', '/ans42'), ('work', '/share/work')]
    print vgen.render_list(numbers.dicts, 'product', 'x', 'y')
    print vgen.render_table(lambda x,y: x*y, range(10), range(10))
    print vgen.render_aggregation(items)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()
    
