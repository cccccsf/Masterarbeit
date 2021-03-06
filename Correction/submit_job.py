#!/usr/bin/python3
import os
import re
import time
import shutil
from Common import record
from Common import rename_file
from Common import submit_job


def if_cal_finish(job):
    path = job.path
    out_file = os.path.join(path, job.method) + '.out'
    if not os.path.exists(out_file):
        return False
    else:
        with open(out_file, 'rb') as f:
            f.seek(-2000, 2)
            lines = f.read().decode('utf-8')
        pattern = 'Molpro calculation terminated'
        termi = re.search(pattern, lines)
        if termi is None:
            return False
        else:
            if termi.group(0) != 'Molpro calculation terminated':
                return False
            return True


def submit(jobs, moni):

    total_num = len(jobs)
    count = 0
    submitted_jobs = []
    finished_jobs = []
    max_calculations_dict = {'12': 5, '28': 3}

    def test_finished(jobs):
        nonlocal count
        nonlocal count_dict
        for job in jobs[:]:
            if if_cal_finish(job):
                finished_jobs.append(job)
                num = str(len(finished_jobs)) + '/' + str(total_num)
                rec = str(job) + '\n'
                rec += num + 'calculation finished.\n'
                rec += '---'*25
                print(rec)
                record(job.root_path, rec)
                jobs.remove(job)
                count -= 1
                count_dict[job.parameter['node']] -= 1

    # test if there is some job which is already finished
    for job in jobs[:]:
        if if_cal_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)
    # test if there is some jobs which are already submitted but not finished
    running_jobs = moni.get_running_jobs()
    for job in jobs[:]:
        if job in running_jobs:
            submitted_jobs.append(job)
            jobs.remove(job)

    # categorize jobs according to the nodes number
    jobs_dict = {}
    count_dict = {}
    nodes_list = []
    for job in jobs:
        node = job.parameter['node']
        if node not in nodes_list:
            nodes_list.append(node)
            jobs_dict[node] = [job]
            count_dict[node] = 0
        else:
            jobs_dict[node].append(job)

    # submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        moni.update_status()
        if len(finished_jobs) == total_num and len(submitted_jobs) == 0:
            break
        else:
            for node in nodes_list:
                if count_dict[node] < max_calculations_dict[node] and len(jobs_dict[node]) > 0:
                    new_job = jobs_dict[node].pop()
                    os.chdir(new_job.path)
                    rename_file(new_job.path, '{}.out'.format(new_job.method))
                    out = submit_job(new_job, new_job.method)
                    count += 1
                    count_dict[node] += 1
                    submitted_jobs.append(new_job)
                    moni.insert_new_job(new_job, out)
                    rec = new_job.path + '\n'
                    rec += new_job.method + '\n'
                    rec += 'job submitted.'
                    rec += '\n' + out + '\n'
                    rec += '---'*25
                    record(new_job.root_path, rec)
                    print(rec)
                else:
                    # time.sleep(0.001)
                    time.sleep(500)
                    # test_calculation(j, jobs, finished_jobs)
                    j += 1
                    if j > 8:
                        rec = 'noting changes.\n'
                        rec += '---'*25
                        record(submitted_jobs[0].root_path, rec)
                        j = 0
                    continue

    return finished_jobs


def test_calculation(j, init_jobs, finished_jobs):
    # ----------------------------------------- test ---------------------------------------------------
    if j >= 2:
        jobs = init_jobs + finished_jobs
        path = r'F:\BlackP\cluster\x_a_5.0\d_int_3.30'
        for job in jobs:
            out_name = job.method + '.out'
            out_from = os.path.join(path, out_name)
            out_to = os.path.join(job.path, out_name)
            shutil.copy(out_from, out_to)
    # ----------------------------------------- test ---------------------------------------------------
