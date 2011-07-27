#!/usr/bin/env python2
"""
relay.py can be used to forward local host TCP connection to remote host
Usage: relay local_host:local_port dest_host:dest_port [dump]
Example:
    relay 127.0.0.1:8000 127.0.0.1:8001      # without dump
    relay 127.0.0.1:8000 127.0.0.1:8001 dump # dump every packet
"""
import sys
import socket
from threading import Thread

class Dump2(Thread):
   def __init__ (self, dest, src, hook):
      Thread.__init__(self)
      self.hook = hook
      self.daemon = True
      self.dest = dest
      self.src = src
      
   def run(self):
      while 1:
          buf = self.src.recv(1024)
          if not buf:
             self.src.close()
             return
          self.hook(buf)
          self.dest.send(buf)

def mk_null_hook(id):
   return lambda x: None

def mk_dump_hook(id):
   def dump(msg):
      print id, ':', repr(msg)
   return dump

def relay(local_host, local_port, dest_host, dest_port, mkhook=mk_null_hook):
   print(('relay: %s:%d -> %s:%d'%(local_host, local_port, dest_host, dest_port)))
   local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   local_socket.bind((local_host, local_port))
   local_socket.listen(1)
   while True:
      try:
         src, addr = local_socket.accept()
         print(('connect: %s:%d'%addr))
         dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         #dest.settimeout(30)
         dest.connect((dest_host, dest_port))
         Dump2(dest, src, hook=mkhook('->')).start()
         Dump2(src, dest, hook=mkhook('<-')).start()
      except KeyboardInterrupt as e:
         print('User Interrupt, Exit...')
         return
      except Exception as e:
         print(e)

class ArgsErr(Exception):
   def __init__(self, msg):
      self.msg = msg
      
   def __str__(self):
      return 'ArgsErr: %s'%(self.msg)
   
if __name__ == '__main__':
   def parse_arg(args):
      if len(args) < 2 or len(args) > 3:
         raise ArgsErr('wrong number of args: %d, expected 2 or 3'%(len(args)))
      src = args[0].split(':')
      dest = args[1].split(':')
      if len(src) == 2: h1, p1 = src
      elif len(src) == 1: h1, p1 = '', src[0]
      else: return None
      assert(len(dest) == 2)
      h2, p2 = dest
      if len(args) == 3: hook = 'null'
      else: hook = args[2]
      mkhook = globals().get('mk_%s_hook'%(args[2]))
      if not hook: raise ArgsErr('no hook defined for %s'% hook)
      return h1, int(p1), h2, int(p2), mkhook
   try:
      h1, p1, h2, p2, mkhook = parse_arg(sys.argv[1:])
   except ArgsErr,e:
      sys.stderr.write('%s\n'% str(e))
      sys.stderr.write(__doc__)
      sys.exit(-1)
   relay(h1, p1, h2, p2, mkhook)
      
