#!/usr/bin/python3
import os
import time
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


def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%b%d_%Y(%H-%M-%S)',timeStruct)


def get_FileCreatTime(file):
    t = os.path.getctime(file)
    return TimeStampToTime(t)


def rename_file(path, file_name):
    record_file = os.path.join(path, file_name)
    if os.path.exists(record_file):
        ctime = get_FileCreatTime(record_file)
        new_name = ctime + '_' + 'record'
        new_name = os.path.join(path, new_name)
        try:
            os.rename(record_file, new_name)
        except FileExistsError as e:
            new_name = ctime + '_' + 'record'+ '1'
            new_name = os.path.join(path, new_name)
            try:
                os.rename(record_file, new_name)
            except Exception as e:
                print(e)

# path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test'
# record(path,'job begins', ll)
# rename_former_record(path)
