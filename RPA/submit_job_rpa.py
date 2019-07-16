#!/usr/bin/python3
import os
import subprocess
import shutil
import time
from Common import record
from Common import submit_job
from Common import rename_file


def copy_submit_src(job):
    ziel_path = job.path
    scr_from = os.path.dirname(os.path.realpath(__file__))
    if job.layertype == 'bilayer':
        scr_from = os.path.join(scr_from, 'job_submit_rpa.bash')
    else:
        scr_from = os.path.join(scr_from, 'job_submit_rpa_layer.bash')
    try:
        scr_to = os.path.join(ziel_path, 'rpa')
        shutil.copy(scr_from, scr_to)
    except Exception as e:
        print(e)
        print('scr copy failed...')


def submit_rpa_job():
    chmod = 'chmod u+x rpa'
    subprocess.call(chmod, shell=True)
    try:
        out_bytes = subprocess.check_output(['qsub', 'rpa'])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    print('job submitted...')
    print(out_text)
    return out_text


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
            # print(last)
            return False


def submit(jobs, moni):
    job_num = len(jobs)
    count = 0
    submitted_jobs = []
    finished_jobs = []
    max_calculations_dict = {'1': 2, '6': 1, '12': 5, '28': 3}

    def test_finished(jobs):
        """
        test jobs which have benn submittdt is finished or not
        if a job finished, add it to list finished_jobs, and delete it from list submitted_jobs
        :param jobs:
        :return:
        """
        nonlocal count
        nonlocal count_dict
        for job in jobs[:]:
            if if_cal_finish(job):
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
        if if_cal_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)

    # categorize jobs according to the nodes number
    jobs_dict = {}
    count_dict = {}
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
        test_finished(submitted_jobs)
        moni.update_status()
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
            # test_calculation(j, jobs, finished_jobs)
            for node in nodes_list:
                if count_dict[node] < max_calculations_dict[node] and len(jobs_dict[node]) > 0:
                    new_job = jobs_dict[node].pop()
                    os.chdir(new_job.path)
                    rename_file(new_job.path, 'rpa.out')
                    out = submit_job(new_job, 'rpa')
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


def test_calculation(j, init_jobs, finished_jobs):
    # ----------------------------------------- test ---------------------------------------------------
    if j >= 2:
        from Common import Job
        # categorization of out jobs
        path = r'F:\BlackP\RPA'
        walks = os.walk(path)
        jobs = []
        for root, dirs, files in walks:
            if 'rpa.out' in files:
                jobs.append(Job(root))
        out_jobs = {}
        for job in jobs:
            if job.layertype not in out_jobs:
                out_jobs[job.layertype] = {}
            if job.x not in out_jobs[job.layertype]:
                out_jobs[job.layertype][job.x] = [job]
            else:
                out_jobs[job.layertype][job.x].append(job)
        for layertype, jobs_dict in out_jobs.items():
            for key, value in jobs_dict.items():
                sorted(value, key=lambda job: float(job.z))

        # categorization of running jobs
        all_jobs = init_jobs + finished_jobs
        runing_jobs_dict = {}
        for job in all_jobs:
            if job.layertype not in runing_jobs_dict:
                runing_jobs_dict[job.layertype] = {}
            if job.x not in runing_jobs_dict[job.layertype]:
                runing_jobs_dict[job.layertype][job.x] = [job]
            else:
                runing_jobs_dict[job.layertype][job.x].append(job)

        # find corresponding jobs
        for layertype, jobs_dict in runing_jobs_dict.items():
            for x, job_list in jobs_dict.items():
                corr_list = out_jobs[layertype]['%.1f' % (float(x)*10+2.5)]
                job_list = sorted(job_list, key=lambda job: float(job.z))
                for i in range(len(job_list)):
                    out_from = corr_list[i].path
                    out_from = os.path.join(out_from, 'rpa.out')
                    out_to = job_list[i].path
                    out_to = os.path.join(out_to, 'rpa.out')
                    shutil.copy(out_from, out_to)
    # ----------------------------------------- test ---------------------------------------------------


if __name__ == '__main__':
    test_calculation(3,1,1)

