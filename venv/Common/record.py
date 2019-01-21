#!/usr/bin/python3
import os
from datetime import datetime


def record(path, content, init = False, begin_time = 0):
    now = datetime.now()
    if begin_time != 0:
        prossing_time = now - begin_time
    now = now.strftime("%b %d %Y %H:%M:%S")
    record_file = os.path.join(path, 'record')
    if init == False:
        with open(record_file, 'a') as f:
            f.write('TIME: '.ljust(10))
            f.write(now)
            f.write('\n')
            f.write(content)
            f.write('\n')
    else:
        with open(record_file, 'w') as f:
            f.write('TIME: '.ljust(10))
            f.write(now)
            f.write('\n')
            f.write(content)
            f.write('\n')


# path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test'
# record(path,'job begins', ll)
