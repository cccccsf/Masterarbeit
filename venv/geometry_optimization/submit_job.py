#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time
import datetime
from Common import record


def submit_geo_opt_job():
    chmod = 'chmod u+x geo_opt.bash'
    command = 'qsub geo_opt.bash'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)
    print('job submitted...')


def copy_fort9(job):
    ziel_path = job.path
    z_dirname = job.z_dirname
    x_dirname = job.x_dirname
    fort9_path = ziel_path.replace(z_dirname, 'z_0')
    fort9_path = fort9_path.replace(x_dirname, 'x_0')
    fort9_from = os.path.join(fort9_path, 'fort.9')
    fort9_to = os.path.join(ziel_path, 'fort.9')
    try:
        shutil.copy(fort9_from, fort9_to)
        print('fort.9 file copied...')
    except Exception as e:
        print(e)
        print('fort.9 failed to copy...')


def copy_submit_scr(job):
    ziel_path = job.path
    scr_path = os.path.dirname(os.path.realpath(__file__))
    scr_from = os.path.join(scr_path, 'job_submit.bash')
    scr_to = os.path.join(ziel_path, 'geo_opt.bash')
    shutil.copy(scr_from, scr_to)
    print('Submition file copied...')


def if_cal_finish(job):
    """
    check the calculation is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    path = job.path
    out_file = os.path.join(path, 'geo_opt.out')
    if not os.path.exists(out_file):
        return False
    else:
        file = open(out_file, 'r')
        lines = file.read().replace('\n', ':')
        lines = ' '.join(lines.split()) + '#'
        regex = 'TOTAL CPU TIME'
        line = re.search(regex, lines)
        if line == None:
            return False
        else:
            if line.group(0) != 'TOTAL CPU TIME':
                return False
            else:
                return True
    return True


def submit(jobs):
    job_numbers = len(jobs)
    max_paralell = 5
    count = 0
    submitted_jobs = []
    finished_jobs = []

    loc = 0
    for job in jobs:
        if job.x == '0' and job.z == '0':
            break
        loc += 1

    job_init = jobs.pop(loc)
    copy_submit_scr(job)
    submit_geo_opt_job()
    submitted_jobs.append(job_init)
    rec = job_init.path
    rec += '\n'
    rec += 'job submitted...'
    record(job_init.root_path, rec)
    r = 0
    while True:
        finished = test_finished(job_init)
        if finished == True:
            rec = job_init.path
            rec += '\n'
            rec += 'calculation finished...'
            record(job_init.root_path, rec)
            break
        else:
            time.sleep(500)
            r += 1
            if r > 15:
                rec = job_init.path
                rec += '\n'
                rec += 'calculation still not finished...'
                record(job_init.root_path, rec)
                r = 0
            continue


    def test_finished(paths):
        for path in paths:
            if if_cal_finish(path):
                finished_jobs.append(path)
                rec = path.path
                rec += '\n'
                rec += 'calculation finished...'
                print(rec)
                record(path.root_path, rec)
                paths.remove(path)
                count -= 1
            else:
                pass

    i = 0
    j = 0
    while i < job_numbers:
        test_finished(submitted_jobs)
        if count <= max_paralell:
            print(jobs[i].path)
            os.chdir(jobs[i].path)
            copy_submit_scr(jobs[i])
            copy_fort9(jobs[i])
            submit_geo_opt_job()
            count += 1
            submitted_jobs.append(jobs[i])
            i += 1
            rec = jobs[i].path + '\n'
            rec += 'job submitted...'
            record(jobs[i].root_path, rec)
        else:
            time.sleep(500)
            if j > 15:
                rec += 'noting changes...'
                record(job_init.root_path, rec)
                j = 0
            continue

    return finished_jobs


# path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\geo_opt\\x_-0.150\\z_-0.106'
# path = job_path.Job_path(path)
# aa = if_cal_finish(path)
# print(aa)
