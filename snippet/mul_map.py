#!/usr/bin/env python

import os
import pickle
from copy import deepcopy

class MulMap:
    def __init__(self, file, recreate=False):
        self.file = file + ".mmp"
        self.dict_list = self._load(recreate)

    def __del__(self):
        self._dump()

    def _load(self, recreate):
        if not os.path.exists(self.file) or recreate:
            return list()
        file = open(self.file, "r")
        return pickle.load(file)

    def _dump(self):
        file = open(self.file, "w")
        pickle.dump(self.dict_list, file)
        
    def add(self, record):
        if record in self.dict_list:
            return
        self.dict_list.append(record)

    def remove(self, record):
        try:
            self.dict_list.remove(record)
        except ValueError:
            pass

    def get(self, **kw):
        return deepcopy([item for item in self.dict_list if self._match(item, kw)])

    @staticmethod
    def _match(item, kw):
        return set(kw.items()) <= set(item.items())
        
    def __str__(self):
        return "%s"%(self.dict_list)

if __name__ == '__main__':
    mul_map =  MulMap("test")
    item1 = {"prog":"fft", "time":2.0}
    item2 = {"prog":"mandel", "time":2.0}
    item3 = {"prog":"fft", "time":3.0}
    mul_map.add(item1)
    mul_map.add(item2)
    mul_map.add(item3)
    print mul_map.get(prog="fft")
    # result = mul_map.get()
    # print result
