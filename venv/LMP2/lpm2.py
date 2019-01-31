#!/usr/bin/python3
import os
import sys
import LMP2
from HF1 import read_init_dis
from Common import record
from Common import ReadIni


def lmp2(path):

    rec = 'LMP2 calculation begins...'
    print(rec)
    record(path, rec)

    init_dist = read_init_dis(path)
    ini_path = os.path.dirname(__file__)
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read basic computation infomation
    if ini_file:
        hf2_jobs = LMP2.get_jobs(path)

        Ini = ReadIni(ini_path)
        nodes = Ini.get_lmp2_info()
        if nodes == '' or nodes == 'default':
            nodes = 1
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    #catagorization
    bilayer = []
    singlelayer = []
    for job in hf2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    #generation of all input files and copy needed files
    for job in bilayer:
        Inp = LMP2.Lmp2_Input(job)
        Inp.write_input()
        LMP2.copy_files(job, nodes)
    for job in singlelayer:
        Inp = LMP2.Lmp2_Input_Layer(job)
        Inp.write_input()
        LMP2.copy_files(job, nodes)

    #submit the jobs
    lmp2_jobs = []
    for job in bilayer:
        new_path = job.path
        new_path = new_path.replace('hf2', 'lmp2')
        new_job = Job_path(new_path)
        lmp2_jobs.append(new_job)
    for job in singlelayer:
        new_path = job.path
        new_path = new_path.replace('hf2', 'lmp2')
        new_job = Job_path(new_path)
        lmp2_jobs.append(new_job)
    finished_jobs_lmp2 = LMP2.submit(lmp2_jobs)

    #read calculation results
    if finished_jobs_lmp2 != []:
        LMP2.read_all_results_lmp2(finished_jobs_lmp2, init_distance = init_dist)

    print('LMP2 calculation finished!!!')
    record(path, 'LMP2 calculation finished!!!')
