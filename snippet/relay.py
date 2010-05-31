#!/usr/bin/python

import socket
from threading import Thread

local_host = ''                 # Symbolic name meaning all available interfaces
local_port = 10000
local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_socket.bind((local_host, local_port))
local_socket.listen(1)
src, addr = local_socket.accept()
print 'conn from:', addr

dest_host = '10.10.108.7'
dest_port = 22
dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest.connect((dest_host, dest_port))

class Dump2(Thread):
   def __init__ (self,dest, src):
      Thread.__init__(self)
      self.dest = dest
      self.src = src
      
   def run(self):
      while 1:
          buf = self.src.recv(1024)
          self.dest.send(buf)

Dump2(dest, src).start()
Dump2(src, dest).start()
