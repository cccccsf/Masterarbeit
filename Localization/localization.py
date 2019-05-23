#!/usr/bin/python3
import sys
import Localization
from Common import record
from Common import ReadIni


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

    # copy input file of localization
    loc_jobs = []
    if len(hf1_jobs) != 0:
        try:
            for job in hf1_jobs:
                if not Localization.if_loc_finish(job):
                    Localization.copy_inp_file(job)
                    Localization.copy_loc_scr(job, nodes, crystal_path)
                    loc_jobs.append(job)
        except Exception as e:
            print(e)
    else:
        print('There is no appropriate Hartree Fock calculation results!!! ')
        print('Program will exit and correct the error and restart from localization step!!!')
        sys.exit(1)

    # submit all jobs
    if len(loc_jobs) > 0:
        loc_finished_job = Localization.submit(loc_jobs)

    rec = 'Localization finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)
