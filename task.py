from render import *

def test_control():
    numbers = dc_map(dict_merge, [dict(x=v) for v in range(3)], [dict(y=v) for v in range(3)])
    numbers = [dict_updated_by_callables(d, product=lambda x,y,**kw: x*y) for d in numbers]
    print(render_list_as_html(numbers, 'x','y', 'product'))
    print(render_table(lambda x,y:x*y, list(range(3)), list(range(3))))
    collpsed = ds_zip(numbers, lambda d,*ds: d['x']*d['y'], 'y', 'x')
    print(render_ds_simple(collpsed, 'x'))
    print(render_list_as_html(collpsed, 'x', *list(range(4))))

def test_msh():
    hosts = dc_map(dict_merge, [dict(host='host%d'% i) for i in range(3)], [dict(user='user%d'% i) for i in range(3)])
    # msh_run(hosts, 'echo', '$host')
    print(render_ds_simple(msh_vrun(hosts, 'host', 'user', 'echo $user@$host'), 'host'))
             
def test_container():
    views = [('home', '/ans42'), ('work', '/share/work')]
    print(render_panels(views))
    print(render_tabs(views))

