#!/usr/bin/python3
import os
import time
import subprocess
from Common import record
from Common import rename_file


def submit_job(job, method=''):
    """
    submit job to PBS system
    :param job: Components.Job
    :param method: name of submit file
    :return:
    """
    path = job.path
    if method == '':
        method = job.method
    os.chdir(path)
    try:
        chmod = 'chmod u+x {}'.format(method)
        subprocess.call(chmod, shell=True)
        out_bytes = subprocess.check_output(['qsub', method])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    except FileNotFoundError as e:
        print(e)
        print('Windows Test.')
        out_text = '*****.rigi'
        return out_text
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    return out_text


def submit(jobs, moni, if_finish_func, method='lmp2'):
    job_num = len(jobs)
    count = 0
    submitted_jobs = []
    finished_jobs = []
    max_calculations_dict = {'1': 6, '6': 2, '12': 5, '28': 3}

    def test_finished(jobs):
        """
        test jobs which have benn submitted is finished or not
        if a job finished, add it to list finished_jobs, and delete it from list submitted_jobs
        :param jobs:
        :return:
        """
        nonlocal count
        nonlocal count_dict
        for job in jobs[:]:
            if if_finish_func(job):
                finished_jobs.append(job)
                num = str(len(finished_jobs)) + '/' + str(job_num)
                rec = str(job)
                rec += '\n'
                rec += num + '  calculation finished.\n'
                rec += '---'*25
                print(rec)
                record(job.root_path, rec)
                jobs.remove(job)
                count -= 1
                count_dict[job.parameter['nodes']] -= 1

    # test if there is some job which is already finished
    for job in jobs[:]:
        if if_finish_func(job):
            finished_jobs.append(job)
            jobs.remove(job)
    # test if there is some jobs which are already submitted but not finished
    running_jobs = moni.get_running_jobs()
    for job in jobs[:]:
        if job in running_jobs:
            submitted_jobs.append(job)
            jobs.remove(job)

    # categorize jobs according to the nodes number
    jobs_dict = {}      # jobs dict according to the specific node
    count_dict = {}     # number of submitted jobs for each specific node
    nodes_list = []
    for job in jobs:
        node = job.parameter['nodes']
        if node not in nodes_list:
            nodes_list.append(node)
            jobs_dict[node] = [job]
            count_dict[node] = 0
        else:
            jobs_dict[node].append(job)

    # submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)   # update list finished_jobs and list submitted_jobs
        moni.update_status()
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
            # test_calculation(j, jobs, finished_jobs)
            for node in nodes_list:
                if count_dict[node] < max_calculations_dict[node] and len(jobs_dict[node]) > 0:
                    new_job = jobs_dict[node].pop()
                    os.chdir(new_job.path)
                    rename_file(new_job.path, '{}.out'.format(method))
                    out = submit_job(new_job, '{}'.format(method))
                    count += 1
                    count_dict[node] += 1
                    submitted_jobs.append(new_job)
                    moni.insert_new_job(new_job, out)
                    rec = str(new_job) + '\n'
                    rec += 'job submitted.'
                    rec += '\n' + out + '\n'
                    rec += '---'*25
                    record(new_job.root_path, rec)
                    print(rec)
                else:
                    # time.sleep(0.01)
                    time.sleep(500)
                    j += 1
                    if j > 15:
                        rec = 'noting changes.\n'
                        rec += '---'*25
                        record(submitted_jobs[0].root_path, rec)
                        j = 0
                    continue

    return finished_jobs
