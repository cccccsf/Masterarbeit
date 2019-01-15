#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time


def copy_submit_src(job):
    ziel_path = job.path
    scr_from = os.path.dirname(os.path.realpath(__file__))
    if job.layertype == 'bilayer':
        scr_from = os.path.join(scr_from, 'job_submit_rpa.bash')
    else:
        scr_from = os.path.join(scr_from, 'job_submit_rpa_layer.bash')
    try:
        scr_to = os.path.join(ziel_path, 'rpa.bash')
        shutil.copy(scr_from, scr_to)
    except Exception as e:
        print(e)
        print('scr copy failed...')

def submit_rpa_job():
    chmod = 'chmod u+x rpa.bash'
    command = 'qsub rpa.bash'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)


def if_cal_finish(job):
    path = job.path
    out_path = os.path.join(path, 'rpa.out')
    if not os.path.exists(out_path):
        return False
    else:
        with open(out_path, 'rb') as f:
            f.seek(-300, 2)
            out = f.read().decode('utf-8')
        out = out.split('\n')
        if out[-1] == '':
            last = out[-2]
        else:
            last = out[-1]
        if last == ' Molpro calculation terminated':
            return True
        else:
            return False


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
            if not os.path.exists('rpa.bash'):
                print('wrong path:')
                print(jobs[i].path)
            else:
                #submit_rpa_job()
                count += 1
                submitted_jobs.append(jobs[i])
                i += 1
        else:
            time.sleep(500)
            continue

    return finished_jobs

