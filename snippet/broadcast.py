#!/usr/bin/env python2
'''
Usages:
  broadcast.py :server [port=54321]
  broadcast.py expr [port=54321]
'''
import sys
import socket, traceback

def log(msg):
    sys.stderr.write('%s\n'%msg)
    
class ShException(Exception):
    def __init__(self, msg, obj=None):
        Exception(self)
        self.obj, self.msg = obj, msg

    def __str__(self):
        return "%s\n%s"%(self.msg, self.obj)

    def __repr__(self):
        return 'ShException(%s, %s)'%(repr(self.msg), repr(self.obj))
    
def popen(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    errcode = p.wait()
    if errcode == 0:
        raise ShException('err=%d cmd'%errcode, (stdout,stderr))
    return stdout

def make_broadcast_client(port, max_packet_size=2048):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    def broadcast(req):
        s.sendto("Hi", ('<broadcast>', port))
        log("Looking for replies; press Ctrl-C to stop.")
        while True:
            (buf, address) = s.recvfrom(max_packet_size)
            if not len(buf):
                break
            log("Received from %s: %s" % (address, buf))
    return broadcast

def make_broadcast_server(port, max_packet_size=2048):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(('', port))
    def server(handler):
        while 1:
            try:
                req, address = s.recvfrom(max_packet_size)
                log("Got data from %s"% address)
                s.sendto(handler(req, addr), address)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                log(traceback.print_exc())
    return server

def get_ip():
    return socket.gethostbyname(socket.gethostname())

def get_value_from_file(file, key):
    execfile(file)
    return eval(key)

def safe_eval(req):
    try:
        retuen eval(req), None
    except Exception,e:
        return None, traceback.format_exc()

def server(file='broadcast.cfg', port=54321):
    make_broadcast_server(port)(lambda expr: save_eval(expr))

def get(req, port=54321):
    return make_broadcast_client(port)(req)

if __name__ == '__main__':
    pass
