#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time



def submit_lmp2_job():
    chmod = 'chmod u+x lmp2.bash'
    command = 'qsub lmp2.bash'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)


def copy_fort80(ziel_path):
    original_path = ziel_path.replace('lmp2', 'hf_1')
    try:
        fort80_to = os.path.join(ziel_path, 'fort.80')
        fort80_from = os.path.join(original_path, 'fort.80')
        shutil.copy(fort80_from, fort80_to)
        print('fort.80 copied...')
    except Exception as e:
        print(e)
        print('fort.80 failed to copy...')


def copy_fort9_fort78(ziel_path):
    original_path = ziel_path.replace('lmp2', 'hf_2')
    try:
        fort9_from = os.path.join(original_path, 'fort.9')
        fort9_to = os.path.join(ziel_path, 'fort.9')
        fort78_from = os.path.join(original_path, 'fort.78')
        fort78_to = os.path.join(ziel_path, 'fort.78')
        shutil.copy(fort9_from, fort9_to)
        shutil.copy(fort78_from, fort78_to)
        print('fort.9 and fort.78 copied...')
    except Exception as e:
        print(e)
        print('fort.9 and fort.78 failed to copy...')


def copy_submit_src(ziel_path):
    scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_lmp2.bash'
    try:
        scr_to = os.path.join(ziel_path, 'lmp2.bash')
        shutil.copy(scr_path, scr_to)
        print('Submition file copied...')
    except Exception as e:
        print(e)
        print('submit scr failed to copy...')


def copy_submit_src_layer(ziel_path):
    scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_lmp2_layer.bash'
    try:
        scr_to = os.path.join(ziel_path, 'lmp2.bash')
        shutil.copy(scr_path, scr_to)
        print('Submition file copied...')
    except Exception as e:
        print(e)
        print('copy failed...')


def copy_files(path):
    ziel_path = path.path.replace('hf_2', 'lmp2')
    if path.layertype == 'bilayer':
        copy_submit_src(ziel_path)
    else:
        copy_submit_src_layer(ziel_path)
    copy_fort80(ziel_path)
    copy_fort9_fort78(ziel_path)


def if_cal_finish(job):
    path = job.path
    out_path = os.path.join(path, 'lmp2.out')
    if not os.path.exists(out_path):
        return False
    else:
        with open(out_path, 'rb') as f:
            f.seek(-1000, 2)
            out = f.read().decode('utf-8')
        regex = 'TERMINATION  DATE'
        termination = re.search(regex, out)
        if termination == None:
            return False
        else:
            if termination.group(0) != 'TERMINATION  DATE':
                return False
            else:
                return True


def submit(jobs):
    max_paralell = 5
    count = 0
    submitted_jobs = []
    finished_jobs = []

    def test_finished(paths):
        """
        test jobs which have benn submittdt is finished or not
        if a job finished, add it to list finished_jobs, and delete it from list submitted_jobs
        :param submitted_jobs:
        :return:
        """
        for path in paths:
            if if_cal_finish(path):
                finished_jobs.append(path)
                print(path)
                print('calculation finished..')
                paths.remove(path)
                count -= 1
            else:
                pass
    i = 0
    while i < len(jobs):
        test_finished(submitted_jobs)   #update list finished_jobs and list submitted_jobs
        if count <= max_paralell:       #check the number of jobs which is running now
            os.chdir(jobs[i].path)
            if not os.path.exists('lmp2.bash'):
                print('wrong path:')
                print(jobs[i].path)
            else:
                #submit_lmp2_job()
                count += 1
                submitted_jobs.append(jobs[i])
                i += 1
        else:
            time.sleep(500)
            continue

    return finished_jobs

