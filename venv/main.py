#!/usr/bin/python3
import os
import shutil
import Pipeline
from Common import ReadIni
from Common import record

def menu():

    ini_path = os.path.dirname(__file__)
    Ini = ReadIni(ini_path)
    path, start, end = Ini.get_initialization_info()

    method = {'hf2': 3, 'hf_2': 3, 'hf_1': 1, 'hf1': 1, 'geo_opt': 0, 'lmp2': 4, 'rpa': 5, 'lrpa': 5, 'localization': 2, 'loc': 2}
    if start == '' or start == 'default':
        start = 0
    else:
        start = start.lower()
        start = method[start]
    if end == '' or end == 'default':
        end = 8
    else:
        end = end.lower()
        end = method[end]

    rec = 'Project begins...'
    record(path, rec, init = True)
    try:
        shutil.copy(ini_path+'/input.ini', path+'/input.ini')
    except Exception as e:
        print(e)

    Pipeline.pipeline(path, start, end)









if  __name__ == "__main__":
    menu()
