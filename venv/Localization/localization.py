#!/usr/bin/python3
import sys
import Localization
from Common import record
from Common import ReadIni


def localization(path):

    rec = 'Geometry Optimization begins...'
    print(rec)
    record(path, rec)


    hf1_jobs = Localization.get_jobs(path)

    ini_path = os.path.dirname(__file__)
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read info
    if ini_file:
        Ini = ReadIni(ini_path)
        nodes = Ini.get_loc_info()
        if nodes == '' or nodes == 'default':
            nodes = 1

    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    #copy input file of localiztion
    loc_jobs = []
    if len(hf1_jobs) != 0:
        try:
            for job in hf1_jobs:
                if not Localization.if_loc_finish(job):
                    Localization.copy_inp_file(job)
                    Localization.copy_loc_scr(job, nodes)
                    loc_jobs.append(job)
        except Exception as e:
            print(e)
    else:
        print('There is no appropriate Hartree Fock calculation results!!! ')
        print('Programm will exit and correct the error and restart from localization step!!!')
        try:
            sys.exit(1)
        except:
            print('Program Exits.')

    #submit all jobs
    loc_finished_job = Localization.submit(loc_jobs)

    print('Hartree Fock calculation 1 finished!!!')
    record(path, 'Hartree Fock calculation 1 finished!!!')
