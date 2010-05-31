#!/usr/bin/env python

from exceptions import Exception
import os
import pickle
from copy import deepcopy

class FileStore:
    def __init__(self, file, reset=False):
        self.file = file + ".store"
        self.mem = self._load(reset)

    def __del__(self):
        self._dump()
        
    def get(self, addr):
        if self.mem.has_key(addr):
            return deepcopy(self.mem[addr])
        else:
            return None

    def set(self, addr, content):
        self.mem[addr] = deepcopy(content)

    def _load(self, reset):
        if not os.path.exists(self.file) or reset:
            return {}
        file = open(self.file, "r")
        return pickle.load(file)

    def _dump(self):
        file = open(self.file, "w")
        pickle.dump(self.mem, file)
        
    def __getitem__(self, addr):
        return self.get(addr)

    def __setitem__(self, addr, content):
        self.set(addr, content)
        
    def __str__(self):
        return "FileStore{file=%s, mem=%s}"%(self.file, self.mem)

class Cache:
    def __init__(self, normal, backup):
        self.normal, self.backup = normal, backup

    def get(self, addr):
        content = self.normal[addr]
        if content:
            print "cached",addr
            return content
        content = self.backup[addr]
        if content:
            self.normal[addr] = content
        return content

    def set(self, addr, content):
        self.normal[addr] = content

    def __getitem__(self, addr):
        return self.get(addr)

    def __setitem__(self, addr, content):
        self.set(addr, content)
