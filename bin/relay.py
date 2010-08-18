#!/usr/bin/python

import sys
import exceptions
import socket
from threading import Thread

class Dump2(Thread):
   def __init__ (self,dest, src):
      Thread.__init__(self)
      self.dest = dest
      self.src = src
      
   def run(self):
      while 1:
          buf = self.src.recv(1024)
          self.dest.send(buf)

def relay(local_host, local_port, dest_host, dest_port):
   local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   local_socket.bind((local_host, local_port))
   local_socket.listen(1)
   while True:
      try:
         src, addr = local_socket.accept()
         dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         dest.connect((dest_host, dest_port))
         Dump2(dest, src).start()
         Dump2(src, dest).start()
      except exceptions.KeyboardInterrupt,e:
         print 'User Interrupt, Exit...'
         return
      except exceptions.Exception,e:
         print e

if __name__ == '__main__':
   def parse_arg(args):
      src = args[0].split(':')
      dest = args[1].split(':')
      if len(src) == 2: h1, p1 = src
      elif len(src) == 1: h1, p1 = '', src[0]
      else: return None
      assert(len(dest) == 2)
      h2, p2 = dest
      return h1, int(p1), h2, int(p2)
   print "relay local_host:local_port dest_host:dest_port"
   relay(*parse_arg(sys.argv[1:]))
      
