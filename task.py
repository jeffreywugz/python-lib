from msite import *

def test_vgen():
    numbers = dcmap(dmerge, [dict(x=i) for i in range(10)], [dict(y=i) for i in range(10)])
    def product(x, y): return x*y
    lset(numbers, 'product', product) 
    items = [('root','/'), ('home', '/ans42'), ('work', '/share/work')]
    print vgen.render_list(numbers, 'product', 'x', 'y')
    print vgen.render_table(lambda x,y: x*y, range(10), range(10))
    print vgen.render_aggregation(items)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()
    
