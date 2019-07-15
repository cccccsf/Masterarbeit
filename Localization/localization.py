#!/usr/bin/python3
import sys
import Localization
from Common import record
from Common import ReadIni
from Common import Job_path
from Common import mkdir


def localization(path):

    rec = 'Localization begins.\n'
    rec += '---'*25
    print(rec)
    record(path, rec)

    # read infos from input.ini file
    Ini = ReadIni()
    nodes, crystal_path = Ini.get_loc()
    if nodes == '' or nodes == 'default':
        nodes = 1
    hf1_jobs = Localization.get_jobs(path)
<<<<<<< HEAD
    ini_path = os.path.dirname(__file__)
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read info
    if ini_file:
        Ini = ReadIni(ini_path)
        nodes, crystal_path = Ini.get_loc_info()
        if nodes == '' or nodes == 'default':
            nodes = 1

    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    #copy input file of localiztion
=======

    # copy input file of localization
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
    loc_jobs = []
    new_loc_jobs = []
    if len(hf1_jobs) != 0:
        try:
            for job in hf1_jobs:
                new_job = job.path.replace('hf1', 'loc')
                new_job = Job_path(new_job)
                new_job.path = job.path
                loc_jobs.append(new_job)
                if not Localization.if_loc_finish(new_job):
                    #mkdir(new_job.path)
                    Localization.copy_inp_file(new_job)
                    Localization.copy_loc_scr(new_job, nodes, crystal_path)
                    new_loc_jobs.append(new_job)
        except Exception as e:
            print(e)
    else:
        print('There is no appropriate Hartree Fock calculation results!!! ')
<<<<<<< HEAD
        print('Programm will exit and correct the error and restart from localization step!!!')
        try:
            sys.exit(1)
        except:
            print('Program Exits.')
    
    #submit all jobs
    loc_finished_job = Localization.submit(new_loc_jobs)
=======
        print('Program will exit and correct the error and restart from localization step!!!')
        sys.exit(1)

    # submit all jobs
    if len(loc_jobs) > 0:
        loc_finished_job = Localization.submit(loc_jobs)
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad

    rec = 'Localization finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)
