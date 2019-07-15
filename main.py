#!/usr/bin/python3
import os
import shutil
import Pipeline
from datetime import datetime
from Common import ReadIni
from Common import record
from Common import rename_file
from Common import mkdir


def menu():

    ini_path = os.path.dirname(os.path.realpath(__file__))
    ini_path = os.path.join(ini_path, 'input.ini')

    Ini = ReadIni(ini_path)
    path = Ini.project_path
    start = Ini.start
    end = Ini.end
    test_begin(end, start)

    now = datetime.now()
    now = now.strftime("%b %d %Y %H:%M:%S")
    mkdir(path)
    rec = 'Project begins.'
    rec += '\n' + '***'*25
    rename_file(path, 'record')
    record(path, rec, init=True)
    print('***'*25)
    print(now)
    print(rec)
    try:
        shutil.copy(ini_path, path + '/input.ini')
    except Exception as e:
        print(e)

    Pipeline.pipeline(path, start, end)


def test_begin(end, start):
    from Common import is_number
    assert is_number(start)
    assert is_number(end)


if __name__ == "__main__":
    menu()
