from msite import *

def test_vgen():
    numbers = algo.dcmap(algo.dmerge, [dict(x=i) for i in range(10)], [dict(y=i) for i in range(10)])
    algo.lset(numbers, 'product', lambda env: env['x'] * env['y']) 
    print vgen.render_list(numbers, 'product', 'x', 'y')
    print vgen.render_table(lambda x,y: x*y, range(10), range(10))

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()
    
