#!/usr/bin/python3
import os
import sys
import RPA
from HF1 import read_init_dis
from Common import record
from Common import ReadIni


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
