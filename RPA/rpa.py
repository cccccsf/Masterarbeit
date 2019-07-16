#!/usr/bin/python3
import RPA
from HF1 import read_init_dis
from Common import record
from Common import ReadIni
from Common import Job


def rpa(path, moni):

    rec = 'LRPA begins.\n'
    rec += '---'*25
    print(rec)
    record(path, rec)

    # read basic computation information
    init_dist = read_init_dis(path)
    lmp2_jobs = RPA.get_jobs(path)
    Ini = ReadIni()
    nodes_rpa_b, memory_b, nodes_rpa_s, memory_s, molpro_path, molpro_key = Ini.get_rpa()

    # categorization
    bilayer = []
    singlelayer = []
    for job in lmp2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    # generate inp file and scr file
    rpa_jobs = []
    rpa_jobs_finished = []
    for job in bilayer:
        new_path = job.path
        new_path = new_path.replace('lmp2', 'rpa')
        new_job = Job(new_path)
        new_job.parameter['nodes'] = nodes_rpa_b
        if not RPA.if_cal_finish(new_job):
            Inp = RPA.RPA_Input(job, memory_b)
            Inp.generate_input()
            rpa_jobs.append(new_job)
            Scr = RPA.Scr(new_job, nodes_rpa_b, molpro_key, molpro_path)
            Scr.gen_scr()
        else:
            new_job.status = 'finished'
            rpa_jobs_finished.append(new_job)
    for job in singlelayer:
        new_path = job.path
        new_path = new_path.replace('lmp2', 'rpa')
        new_job = Job(new_path)
        new_job.parameter['nodes'] = nodes_rpa_s
        if not RPA.if_cal_finish(new_job):
            Inp = RPA.RPA_Input(job, memory_s)
            Inp.generate_input()
            Scr = RPA.Scr(new_job, nodes_rpa_s, molpro_key, molpro_path)
            Scr.gen_scr()
            rpa_jobs.append(new_job)
        else:
            new_job.status = 'finished'
            rpa_jobs_finished.append(new_job)

    # submit the jobs
    if len(rpa_jobs) > 0:
        new_finished_jobs = RPA.submit(rpa_jobs, moni)
        rpa_jobs_finished += new_finished_jobs
    # read calculation results
    if len(rpa_jobs_finished) > 0:
        RPA.read_and_record_all_results(rpa_jobs_finished, init_dist)

    rec = 'LRPA finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)
