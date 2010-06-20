from msite import *
from extra import *

def test_control():
    numbers = dcmap(dmerge, [dict(x=v) for v in range(3)], [dict(y=v) for v in range(3)])
    numbers = map(lambda d: dupdated(d, product=lambda x,y,**kw: x*y), numbers)
    print render_list(numbers, 'x','y', 'product')
    print render_table(lambda x,y:x*y, range(3), range(3))
    collpsed = dszip(numbers, lambda d,*ds: d['x']*d['y'], 'y', 'x')
    print render_ds(collpsed, 'x')
    print render_list(collpsed, 'x', *range(4))

def test_msh():
    hosts = dcmap(dmerge, [dict(host='host%d'% i) for i in range(3)], [dict(user='user%d'% i) for i in range(3)])
    # msh_run(hosts, 'echo', '$host')
    print render_ds(msh_vrun(hosts, 'host', 'user', 'echo $user@$host'), 'host')
             
def test_container():
    views = [('home', '/ans42'), ('work', '/share/work')]
    print core_templates.render('panels.html',views=views)
    print core_templates.render('tabs.html', views=views)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()

wiki = Wiki('.')
