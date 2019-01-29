#!/usr/bin/python3
import os
import sys
import Initialization
from copy import deepcopy
from Crystal import Geometry
from Common import mkdir
from Common import Job_path
from Common import record
from Common import ReadIni
from Common import look_for_in_list
import geometry_optimization
import HF1
# import Localization
# import HF2
# import LMP2
# import RPA



def localization(path):

    job_dirs = Localization.copy_inp_loc.get_job_dirs(path)

    #copy input file of localiztion
    if len(job_dirs) != 0:
        Localization.copy_inp_loc.copy_all_files(job_dirs)
    else:
        print('There is no appropriate Hartree Fock calculation results!!! ')
        print('Programm will exit and correct the error and restart from localization step!!!')
        try:
            sys.exit(1)
        except:
            print('Program Exits.')
        finally:
            print('---------------------------------------------------------------------------------------')

    #copy job submit file to each directory
    Localization.submit_job_loc.copy_all_files(job_dirs)
    loc_job_dirs = Localization.submit_job_loc.get_job_dirs(path)
    #submitted_paths = Localization.submit_job_loc.submit(loc_job_dirs)

    #test finished
    while True:
        if Localization.submit_job_loc.test_all_loc_finished(loc_job_dirs):
            print ('Localization finished!')
            break
        else:
            time.sleep(500)
            continue


def hf2(path):

    file = os.path.exists('INPUT')
    job_dirs = HF2.generation_input_hf2.get_job_dirs(path)
    hf1_paths = []
    for job in job_dirs:
        job_path = Job_path(job)
        hf1_paths.append(job_path)

    #catagorization
    bilayer = []
    singlelayer = []
    for job_path in hf1_paths:
        if job_path.layertype == 'bilayer':
            bilayer.append(job_path)
        elif job_path.layertype == 'underlayer' or job_path.layertype == 'upperlayer':
            singlelayer.append(job_path)

    #read basic computation infomation
    if file:
        pass
    else:
        print('INPUT file does not exist!!!')
        print('''Do you want to start initialization or exit?
                 Please enter 1 to start initialization programm and enter 0 to exit the programm''')

    #generation of all input files
    for job in bilayer:
        Inp = HF2.generation_input_hf2.Input(job)
        Inp.gen_input()
        HF2.submit_job_hf2.copy_submit_scr(job)
        HF2.submit_job_hf2.copy_fort9(job)
    for job in singlelayer:
        Inp = HF2.inp_layers_hf2.Layer_Inp(job)
        Inp.gen_input()
        HF2.submit_job_hf2.copy_submit_scr(job)
        HF2.submit_job_hf2.copy_fort9(job)

    #submit the jobs
    hf2_job_dirs = bilayer + singlelayer
    for i in range(len(hf2_job_dirss)):
        hf2_job_dirs[i].reset('method', 'hf_2')
    #submitted_jobs_hf2 = HF2.submit_job_hf2.submit(hf2_job_dirs)

    #read calculation results
    #HF2.read_all_results(submitted_jobs_hf2)

    print('Hartree Fock calculation 2 finished!!!')


def lmp2(path):

    job_paths = LMP2.get_jobs(path)
    hf2_jobs = []
    for p in job_paths:
        job = Job_path(p)
        hf2_jobs.append(job)

    #catagorization
    bilayer = []
    singlelayer = []
    for job in hf2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    #read basic computation infomation
    file = os.path.exists('INPUT')
    if file:
        pass
    # else:
    #
    #     print('INPUT file does not exist!!!')
    #     print('''Do you want to start initialization or exit?
    #              Please enter 1 to start initialization programm and enter 0 to exit the programm''')

    #generation of all input files and copy needed files
    for job in bilayer:
        Inp = LMP2.Lmp2_Input(job)
        Inp.write_input()
        LMP2.copy_files(job)
    for job in singlelayer:
        Inp = LMP2.Lmp2_Input_Layer(job)
        Inp.write_input()
        LMP2.copy_files(job)

    #submit the jobs
    lmp2_jobs = bilayer + singlelayer
    for i in range(len(lmp2_jobs)):
        lmp2_jobs[i].reset('method', 'lmp2')
    #finished_jobs_lmp2 = LMP2.submit(lmp2_jobs)

    #read calculation results
    #LMP2.read_all_results(finished_jobs_lmp2)

    print('LMP2 calculation finished!!!')



def rpa(path):

    jobs = RPA.get_jobs(path)
    lmp2_jobs = []
    for p in jobs:
        job = Job_path(p)
        lmp2_jobs.append(job)

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
    rpa_jobs = bilayer + singlelayer
    for i in range(len(rpa_jobs)):
        rpa_jobs[i].reset('method', 'rpa')
    for job in rpa_jobs:
        RPA.copy_submit_src(job)
    #finished_jobs_rpa = RPA.submit(lmp2_jobs)

    #read calculation results
    #RPA.read_all_results(finished_jobs_rpa)

    print('LRPA calculation finished!!!')


def pipeline(path, start):
    if start == 0:
        geometry_optimization.geo_opt(path)
        start += 1
    if start == 1:
        HF1.hf1(path)
        start += 1
    # if start == 2:
    #     localization(path)
    #     start += 1
    # if start == 3:
    #     hf2(path)
    #     start += 1
    # if start == 4:
    #     lmp2(path)
    #     start += 1
    # if start == 5:
    #     rpa(path)
    #     start += 1
