#!/usr/bin/python3
import os
import Initialization
import Pipeline
from Common import ReadIni
from Common import record

def menu():

    #path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test'
    # path = os.getcwd()
    # path = os.path.dirname(path)
    # path = os.path.join(path, 'Test')
    ini_path = os.path.dirname(__file__)
    Ini = ReadIni(ini_path)
    path = Ini.get_initialization_info()
    Pipeline.pipeline(path)
    rec = 'Project begins...'
    record(rec, init = True)








if  __name__ == "__main__":
    menu()
