#!/usr/bin/python
#
#

import sys
import random

lines = []
for line in sys.stdin:
   lines.append(line)

lines.sort()

length = len(lines)
for l in range(0,length):
   choice = random.randint(0,len(lines)-1)
   #print str(choice) + ' of ' + str(len(lines))
   print lines.pop(choice),
