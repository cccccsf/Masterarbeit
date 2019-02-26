#!/usr/bin/python3
import os
import sys
from copy import deepcopy
from Crystal import Geometry
from Common import mkdir
from Common import Job_path
from Common import record
from Common import ReadIni
import HF1



def hf1(path):

    rec = 'First Hartree Fock Calculation begins...'
    print(rec)
    record(path, rec)

    init_dist = HF1.read_init_dis(path)
    ini_path = os.path.dirname(__file__)
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read basic computation infomation
    if ini_file:
        jobs_GeoOpt = HF1.select_jobs(path)

        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        bs_type, nodes, crystal_path = Ini.get_hf1_info()
        if nodes == '' or nodes == 'default':
            nodes = 12
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    jobs_HF1 = []
    new_jobs = []
    hf1_jobs_finished = []
    #input for the whole system
    #print('number Geo Opt', len(jobs_GeoOpt))
    for job in jobs_GeoOpt:
        path_GeoOpt = job.path
        #Bilayer
        path_HF1 = path_GeoOpt.replace('geo_opt', 'hf1')
        new_job = Job_path(path_HF1)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Input(job, name, slab_or_molecule, group, bs_type, layertype = 'bilayer', fiexed_atoms=fixed_atoms)
            Inp.gen_input()
            HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)
        #upperlayer
        path_upper = os.path.join(path_HF1, 'upperlayer')
        new_job = Job_path(path_upper)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Layer_Inp(job, name, slab_or_molecule, group, bs_type, layertype = 'upperlayer', fiexed_atoms=fixed_atoms)
            Inp.gen_input()
            HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)
        #underlayer
        path_under = os.path.join(path_HF1, 'underlayer')
        new_job = Job_path(path_under)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Layer_Inp(job, name, slab_or_molecule, group, bs_type, layertype = 'underlayer', fiexed_atoms=fixed_atoms)
            Inp.gen_input()
            HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)
    #Submit the calculation job
    hf1_jobs_finished_new = HF1.submit(new_jobs)
    hf1_jobs_finished += hf1_jobs_finished_new

    #read calculation results
    HF1.read_all_results_hf1(hf1_jobs_finished, init_dist)

    print('Hartree Fock calculation 1 finished!!!')
    record(path, 'Hartree Fock calculation 1 finished!!!')
