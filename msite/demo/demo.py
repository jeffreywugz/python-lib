import sys, os
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.extend(os.path.join(cwd, '..'))
from msite import *
template = Template(cwd)

@cherrypy.expose
def msh(expr='True'):
    result = None
    exception = None
    try:
        result = eval(expr, globals(), locals())
    except exceptions.Exception,e:
        exception = e
        result = str(exception)
    return template.render("shell.html", expr=expr, result=result, exception=exception, traceback=traceback.format_exc(10))

config = {'/': {'tools.staticdir.on': True, 'tools.staticdir.dir': cwd, 'tools.safe_multipart.on': True},
          }
