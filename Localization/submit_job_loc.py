#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time
from Common import Job
from Common import record
from Common import submit_job


def submit_loc_job():
    chmod = 'chmod u+x loc'
    subprocess.call(chmod, shell=True)
    try:
        out_bytes = subprocess.check_output(['qsub', 'loc'])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    #print('job submitted...')
    #print(out_text)
    return out_text


def copy_loc_scr(job, nodes, crystal_path):

    ziel_path = job.path
    scr_path = os.path.dirname(__file__)
    scr_from = os.path.join(scr_path, 'loc_job')
    scr_to = os.path.join(ziel_path, 'loc')
    shutil.copy(scr_from, scr_to)
    if nodes != '':
        try:
            nodes = int(nodes)
            update_nodes(ziel_path, nodes, crystal_path)
        except Exception as e:
            print(e)
    print('loc submit scr copied.')


def update_nodes(path, nodes, crystal_path):
    scr = os.path.join(path, 'loc')
    with open(scr, 'r') as f:
        lines = f.readlines()
    nodes_line = lines[3]
    loc = 3
    if nodes_line.startswith('#PBS -l nodes'):
        pass
    else:
        i = 0
        for line in lines:
            if line.startswith('#PBS -l nodes'):
                loc = i
            i += 1
    loc_cry = 0, 0
    j = 0
    for line in lines:
        if line.startswith('crystal_path='):
            loc_cry = j
        j += 1
    if nodes != '':
        nodes_line = '#PBS -l nodes={}\n'.format(nodes)
        lines[loc] = nodes_line
    if crystal_path != '':
        lines[loc_cry] = 'crystal_path={}\n'.format(crystal_path)

    with open(scr, 'w') as f:
        f.writelines(lines)


def copy_all_files(job_dirs, nodes, crystal_path):
    try:
        for job_dir in job_dirs:
            copy_loc_scr(job_dir, nodes, crystal_path)
    except Exception as e:
        print(e)


def if_loc_finish(job):
    path = job.path
    """
    check the localiztion is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    out_file = os.path.join(path, 'loc.out')
    if not os.path.exists(out_file):
        return False
    else:
        with open(out_file, 'r') as f:
            lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split()) + '#'
        regex = 'TERMINATION.*#'
        line = re.search(regex, lines)
        if line is None:
            return False
        else:
            return True


def test_all_loc_finished(job_dirs):
    while True:
        for job_dir in job_dirs:
            if_finished = if_loc_finish(job_dir)
            if if_finished is False:
                return False
        break
    return True


def submit(jobs):

    jobs_len = len(jobs)
    max_paralell = 8
    count = 0
    submitted_jobs = []
    finished_jobs = []

    def test_finished(jobs):
        nonlocal count
        for job in jobs[:]:
            if if_loc_finish(job):
                finished_jobs.append(job)
<<<<<<< HEAD
                num = str(len(finished_jobs)) + '/' + str(jobs_len)
                rec = job.path
                rec += '\n'
                rec += num
                rec += ' localization finished...'
=======
                rec = str(job)
                rec += '\n'
                rec += 'Localization finished.\n'
                rec += '---'*25
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
                print(rec)
                record(job.root_path, rec)
                jobs.remove(job)
                count -= 1

    # test if there is some job which is already finished
    for job in jobs[:]:
        if if_loc_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)

    # submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        if len(finished_jobs) == jobs_len and len(submitted_jobs) == 0:
            break
        else:
            if count <= max_paralell and len(jobs) != 0:
                new_job = jobs.pop()
                os.chdir(new_job.path)
<<<<<<< HEAD
                out = submit_loc_job()
=======
                out = submit_job(new_job, 'loc')
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
                count += 1
                submitted_jobs.append(new_job)
                new_job.method = 'loc'
                rec = str(new_job) + '\n'
                rec += 'job submitted.'
                rec += '\n' + out + '\n'
                rec += '---'*25
                record(new_job.root_path, rec)
                print(rec)
            else:
                time.sleep(500)
                # time.sleep(3)
                j += 1
                test_calculation(j, jobs, submitted_jobs, finished_jobs)    # test function
                if j > 10:
                    rec = 'noting changes.'
                    record(submitted_jobs[0].root_path, rec)
                    j = 0
                continue

    return finished_jobs


def test_calculation(j, init_jobs, submitted_jobs, finished_jobs):
    # ----------------------------------------- test ---------------------------------------------------
    if j >= 2:
        # categorization of out jobs
        path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\hf2'
        walks = os.walk(path)
        jobs = []
        for root, dirs, files in walks:
            if 'loc.out' in files:
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
        all_jobs = init_jobs + finished_jobs + submitted_jobs
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
                    fort_from = os.path.join(out_from, 'fort.80')
                    out_from = os.path.join(out_from, 'loc.out')
                    out_to = job_list[i].path
                    fort_to = os.path.join(out_to, 'fort.80')
                    out_to = os.path.join(out_to, 'loc.out')
                    shutil.copy(out_from, out_to)
                    shutil.copy(fort_from, fort_to)
    # ----------------------------------------- test ---------------------------------------------------


if __name__ == '__main__':
    test_calculation(3,1,1,1)
