#!/usr/bin/python3
import os
import sys
import RPA
from HF1 import read_init_dis
from Common import record
from Common import ReadIni
from Common import Job_path


def rpa(path):

    rec = 'LRPA Calculation begins...'
    print(rec)
    record(path, rec)

    init_dist = read_init_dis(path)
    ini_path = os.path.dirname(os.path.relpath(__file__))
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read basic computation infomation
    if ini_file:
        lmp2_jobs = RPA.get_jobs(path)
        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        nodes_rpa_b, nodes_rpa_s, molpro_key, molpro_path = Ini.get_rpa_info()
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    #catagorization
    bilayer = []
    singlelayer = []
    for job in lmp2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    #generation of all input files
    for job in bilayer:
        Inp = RPA.RPA_Input(job, '12000')
        Inp.generate_input()
    for job in singlelayer:
        Inp = RPA.RPA_Input(job, '2900')
        Inp.generate_input()

    #copy files and submit the jobs
    rpa_jobs = []
    for job in bilayer:
        new_path = job.path
        new_path = new_path.replace('lmp2', 'rpa')
        new_job = Job_path(new_path)
        rpa_jobs.append(new_job)
        Scr = RPA.Scr(job, nodes_rpa_b, molpro_key, molpro_path)
        Scr.gen_scr()
    for job in singlelayer:
        new_path = job.path
        new_path = new_path.replace('lmp2', 'rpa')
        new_job = Job_path(new_path)
        rpa_jobs.append(new_job)
        Scr = RPA.Scr(job, nodes_rpa_s, molpro_key, molpro_path)
        Scr.gen_scr()
    finished_jobs_rpa = RPA.submit(lmp2_jobs)

    #read calculation results
    RPA.read_and_record_all_results(finished_jobs_rpa)

    print('LRPA calculation finished!!!')
    record(path, 'LRPA calculation 2 finished!!!')
