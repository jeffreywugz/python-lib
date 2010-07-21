from msite import *
from extra import *
from render import *

def test_control():
    numbers = dc_map(dict_merge, [dict(x=v) for v in range(3)], [dict(y=v) for v in range(3)])
    numbers = map(lambda d: dict_updated_by_callables(d, product=lambda x,y,**kw: x*y), numbers)
    print render_list_as_html(numbers, 'x','y', 'product')
    print render_table(lambda x,y:x*y, range(3), range(3))
    collpsed = ds_zip(numbers, lambda d,*ds: d['x']*d['y'], 'y', 'x')
    print render_ds(collpsed, 'x')
    print render_list_as_html(collpsed, 'x', *range(4))

def test_msh():
    hosts = dc_map(dict_merge, [dict(host='host%d'% i) for i in range(3)], [dict(user='user%d'% i) for i in range(3)])
    # msh_run(hosts, 'echo', '$host')
    print render_ds(msh_vrun(hosts, 'host', 'user', 'echo $user@$host'), 'host')
             
def test_container():
    views = [('home', '/ans42'), ('work', '/share/work')]
    print render_panels(views)
    print render_tabs(views)

def test_msite():
    app = MsiteApp('.', rpc.RpcDemo(), globals())
    app.run()

wiki = Wiki('.')
