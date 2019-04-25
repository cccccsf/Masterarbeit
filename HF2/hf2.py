#!/usr/bin/python3
import os
import sys
import HF2
from Common import record
from Common import ReadIni
from Common import Job_path
from HF1 import read_init_dis


def hf2(path):

    rec = 'Second Hartree Fock Calculation begins...'
    print(rec)
    record(path, rec)

    init_dist = read_init_dis(path)
    ini_path = os.path.dirname(__file__)
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    # read basic computation infomation
    if ini_file:
        jobs_HF1 = HF2.get_jobs(path)
        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        bs_type, nodes, crystal_path = Ini.get_hf2_info()
        if nodes == '' or nodes == 'default':
            nodes = 12
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    # catagorization
    bilayer = []
    singlelayer = []
    for job in jobs_HF1:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)
<<<<<<< HEAD:venv/HF2/hf2.py
    
    #generation of all input files
=======

    # generation of all input files
>>>>>>> 9837390163629d9445152c2c968b8f8c2d249d30:HF2/hf2.py
    for job in bilayer:
        Inp = HF2.Input(
            job,
            name,
            slab_or_molecule,
            group,
            bs_type=bs_type,
            layertype='bilayer',
            fixed_atoms=fixed_atoms)
        Inp.gen_input()
        HF2.copy_submit_scr(job, nodes, crystal_path)
        HF2.copy_fort9(job)
    for job in singlelayer:
        Inp = HF2.Layer_Inp(
            job,
            name,
            slab_or_molecule,
            group,
            bs_type=bs_type,
            layertype=job.layertype,
            fixed_atoms=fixed_atoms)
        Inp.gen_input()
        HF2.copy_submit_scr(job, nodes, crystal_path)
        HF2.copy_fort9(job)
<<<<<<< HEAD:venv/HF2/hf2.py
    
    #submit the jobs
=======

    # submit the jobs
>>>>>>> 9837390163629d9445152c2c968b8f8c2d249d30:HF2/hf2.py
    hf2_jobs = []
    for job in bilayer:
        new_path = job.path
        new_path = new_path.replace('hf1', 'hf2')
        new_job = Job_path(new_path)
        hf2_jobs.append(new_job)
    for job in singlelayer:
        new_path = job.path
        new_path = new_path.replace('hf1', 'hf2')
        new_job = Job_path(new_path)
        hf2_jobs.append(new_job)
    hf2_jobs_finished = HF2.submit(hf2_jobs)

    # read calculation results
    if hf2_jobs_finished != []:
        HF2.read_all_results_hf2(hf2_jobs_finished, init_dist=init_dist)

    print('Hartree Fock calculation 2 finished!!!')
    recod(path, 'Hartree Fock calculation 2 finished!!!')
