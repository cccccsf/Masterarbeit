#!/usr/bin/python3
import os
import shutil
from Common import Job_path
from HF1 import if_cal_finish


def get_jobs(path):
    path = os.path.join(path, 'hf1')
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if ('hf.out' in files) and ('fort.9' in files):
            new_path = root
            new_job = Job_path(new_path)
            if if_cal_finish(job):
                jobs.append(new_job)
    return jobs


def copy_inp_file(job):

    ziel_path = job.path
    inp_path = os.path.dirname(__file__)
    inp_from = os.path.join(scr_path, 'input.loc')
    inp_to = os.path.join(ziel_path, 'input.loc')
    shutil.copy(inp_from, inp_to)
    print(ziel_path)
    print('input.loc copied...')



