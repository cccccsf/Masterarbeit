#!/usr/bin/python3
import os
import re
import subprocess
import time
from Common import record
from Common import rename_file


def submit_job(job):
    job_name = job.method
    chmod = 'chmod u+x {}'.format(job_name)
    subprocess.call(chmod, shell=True)
    try:
        out_bytes = subprocess.check_output(['qsub', job_name])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    return out_text


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
        if termi == None:
            return False
        else:
            if termi.group(0) != 'Molpro calculation terminated':
                return False
            return True
    return True


def submit(jobs):

    total_num = len(jobs)
    count = 0
    submitted_jobs = []
    finished_jobs = []
    max_calculations_12 = 5
    max_calculations_28 = 3
    max_calculations_dict = {'12': 5, '28': 3}

    def test_finished(jobs):
        nonlocal count
        for job in jobs[:]:
            if if_cal_finish(job):
                finished_jobs.append(job)
                num = str(len(finished_jobs)) + '/' + str(total_num)
                rec = job.path + '\n'
                rec += job.method + '\n'
                rec += num + 'calculation finished...'
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
        test_finished(jobs)
        if len(finished_jobs) == total_num and len(submitted_jobs) == 0:
            break
        else:
            for node in nodes_list:
                if count_dict[node] < max_calculations_dict[node]:
                    new_job = jobs_dict[node].pop()
                    os.chdir(new_job.path)
                    rename_file(new_job.path, '{}.out'.format(new_job.method))
                    out = submit_job(job)
                    count += 1
                    count_dict[node] += 1
                    submitted_jobs.append(new_job)
                    rec = new_job.path + '\n'
                    rec += new_job.method + '\n'
                    rec += 'job submitted...'
                    rec += '\n' + out +'\n'
                    record(new_job.root_path, rec)
                    print(rec)
                else:
                    time.sleep(500)
                    j += 1
                    if j > 8:
                        rec += 'noting changes...\n'
                        record(submitted_jobs[0].root_path, rec)
                        j = 0
                    continue

    return finished_jobs
