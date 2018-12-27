#!/usr/bin/python3
import os
import shutil


def get_job_dirs(path):
    path = path + '/hf_1/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if ('hf.out' in files) and ('fort.9' in files):
            job_dirs.append(root)
    return job_dirs


def copy_inp_file(path):

    scr_path = os.path.dirname(os.path.realpath(__file__)) + '/input.loc'
    shutil.copy(scr_path, path+'/input.loc')
    print(path)
    print('input.loc copied...')


def copy_all_files(job_dirs):

    #job_dirs_with_locinp = []
    try:
        for job_dir in job_dirs:
            copy_inp_file(job_dir)
            #job_dirs_with_locinp.append(job_dir)
    except Exception as e:
        print(e)


