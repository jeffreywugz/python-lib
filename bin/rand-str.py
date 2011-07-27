#!/usr/bin/env python2

import sys
import random
import string

for i in range(int(sys.argv[1])):
    print ''.join(random.sample(string.lowercase, 10))

