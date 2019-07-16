#!/usr/bin/python3
import os
import sys
import LMP2
from HF1 import read_init_dis
from Common import record
from Common import ReadIni
from Common import record_data_json
from Common import Job


def lmp2(path, moni):

    rec = 'LMP2 Calculation begins.\n'
    rec += '---'*25
    print(rec)
    record(path, rec)

    init_dist = read_init_dis(path)
    # read basic computation information
    hf2_jobs = LMP2.get_jobs(path)
    Ini = ReadIni()
    nodes, cryscor_path = Ini.get_lmp2()
    cal_parameters = Ini.get_cal_parameters('LMP2')
    ll = Ini.ll
    if nodes == '' or nodes == 'default':
        nodes = 1
    record_data_json(path, 'nodes', nodes, section='lmp2')

    # categorization
    bilayer = []
    singlelayer = []
    for job in hf2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    # generation of all input files and copy needed files
    lmp2_jobs = []
    lmp2_jobs_finished = []
    for job in bilayer:
        new_path = job.path
        new_path = new_path.replace('hf2', 'lmp2')
        new_job = Job(new_path)
        if not LMP2.if_cal_finish(new_job):
            Inp = LMP2.Lmp2Input(job, ll, cal_parameters)
            Inp.write_input()
            LMP2.copy_files(new_job, nodes, cryscor_path)
            lmp2_jobs.append(new_job)
        else:
            lmp2_jobs_finished.append(new_job)
    for job in singlelayer:
        new_path = job.path
        new_path = new_path.replace('hf2', 'lmp2')
        new_job = Job(new_path)
        if not LMP2.if_cal_finish(new_job):
            Inp = LMP2.Lmp2InputLayer(job, cal_parameters)
            Inp.write_input()
            LMP2.copy_files(new_job, nodes, cryscor_path)
            lmp2_jobs.append(new_job)
        else:
            lmp2_jobs_finished.append(new_job)

    # submit the jobs
    if len(lmp2_jobs) > 0:
        new_finished_jobs = LMP2.submit(lmp2_jobs, moni)
        lmp2_jobs_finished += new_finished_jobs
    # read calculation results
    # if len(lmp2_jobs_finished) > 0:
    #     LMP2.read_all_results_lmp2(lmp2_jobs_finished, init_distance=init_dist)

    rec = 'LMP2 finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)
