#!/usr/bin/python3
import os
import re
import math
import subprocess
import shutil
import time
from Common import record
from Common import rename_file
from Common import submit_job
from Common import Job


def submit_hf1_job():
    chmod = 'chmod u+x hf'
    subprocess.call(chmod, shell=True)
    try:
        out_bytes = subprocess.check_output(['qsub', 'hf'])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    print('job submitted...')
    print(out_text)
    return out_text


def copy_submit_scr(job, nodes, crystal_path, nearest_job=0):
    ziel_path = job.path
    scr_path = os.path.dirname(os.path.realpath(__file__))
    if job.x == '0' and job.z == '0':
        scr_from = os.path.join(scr_path, 'job_submit_init.bash')
    else:
        scr_from = os.path.join(scr_path, 'job_submit.bash')
    scr_to = os.path.join(ziel_path, 'hf')
    shutil.copy(scr_from, scr_to)
    update_nodes(ziel_path, nodes, crystal_path)
    if not isinstance(nearest_job, int):
        insert_path_of_fort9(job, nearest_job)
    print('Submition file copied.')


def insert_path_of_fort9(job, nearest_job):
    submit_file = os.path.join(job.path, 'geo_opt')
    with open(submit_file, 'r') as f:
        lines = f.readlines()
    loc = 0
    for i in range(len(lines)):
        if lines[i].startswith('cp fort.20'):
            loc = i
    # print(lines[loc])
    if job.layertype == 'bilayer':
        path_from = os.path.join('../..', os.path.join(nearest_job.x_dirname, os.path.join(nearest_job.z_dirname, 'fort.9')))
    else:
        path_from = os.path.join('../..', os.path.join(nearest_job.x_dirname, os.path.join(nearest_job.z_dirname, os.path.join(nearest_job.layertype,'fort.9'))))
    # print(path_from)
    line = 'cp {} $currdir/fort.20\n'.format(path_from)
    if loc > 0:
        lines[loc] = line
    with open(submit_file, 'w') as f:
        f.writelines(lines)


def update_nodes(path, nodes, crystal_path):
    scr = os.path.join(path, 'hf')
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
    loc2, loc_cry = 0, 0
    j = 0
    for line in lines:
        if line.startswith('mpirun -np'):
            loc2 = j
        if line.startswith('crystal_path='):
            loc_cry = j
        j += 1
    if nodes != '':
        nodes_line = '#PBS -l nodes={}\n'.format(nodes)
        lines[loc] = nodes_line
        lines[loc2] = 'mpirun -np {} $crystal_path/Pcrystal >& ${{PBS_O_WORKDIR}}/hf.out\n'.format(nodes)
    if crystal_path != '':
        lines[loc_cry] = 'crystal_path={}\n'.format(crystal_path)

    with open(scr, 'w') as f:
        f.writelines(lines)


def copy_fort9(job):
    ziel_path = job.path
    z_dirname = job.z_dirname
    x_dirname = job.x_dirname
    fort9_path = ziel_path.replace(z_dirname, 'z_0')
    fort9_path = fort9_path.replace(x_dirname, 'x_0')
    fort9_from = os.path.join(fort9_path, 'fort.9')
    fort9_to = os.path.join(ziel_path, 'fort.20')
    try:
        shutil.copy(fort9_from, fort9_to)
        print('fort.9 file copied...')
    except Exception as e:
        print(e)
        print('fort.9 failed to copy...')


def if_cal_finish(job):
    """
    check the calculation is finished or not through the output file
    :param job: string
    :return: Bool Ture of False
    """
    path = job.path
    out_file = os.path.join(path, 'hf.out')
    try:
        if not os.path.exists(out_file):
            return False
        else:
            with open(out_file, 'r') as f:
                lines = f.read().replace('\n', ':')
            lines = ' '.join(lines.split()) + '#'
            regex = 'TOTAL CPU TIME'
            line = re.search(regex, lines)
            if line is None:
                return False
            else:
                if line.group(0) != 'TOTAL CPU TIME':
                    return False
                else:
                    return True
    except FileNotFoundError as e:
        return False


def submit(jobs, nodes, crystal_path):
    job_num = len(jobs)
    max_paralell = 5
    count = 0
    submitted_jobs = []
    finished_jobs = []

    def test_finished(jobs):
        nonlocal count
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
                count -= 1
                jobs.remove(job)

    # test if there is some job which is already finished
    for job in jobs[:]:
        if if_cal_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)

    # find and submit the initial job
    # print('number of jobs: ', len(jobs))
    init_jobs = []
    for job in jobs[:]:
        if job.x == '0' and job.z == '0':
            init_jobs.append(job)
            jobs.remove(job)
    for job in init_jobs[:]:
        if not if_cal_finish(job):
            os.chdir(job.path)
            rename_file(job.path, 'hf.out')
            out = submit_job(job, 'hf')
            count += 1
            submitted_jobs.append(job)
            rec = str(job)
            print(rec)
            rec += '\n'
            rec += 'job submitted.'
            rec += '\n' + out + '\n'
            rec += '---'*25
            record(job.root_path, rec)
        else:
            finished_jobs.append(job)
    # detect if init jobs finished
    r = 0
    while True:
        test_finished(submitted_jobs)      # test function
        if len(submitted_jobs) == 0:
            break
        else:
            time.sleep(500)
            r += 1
            if r > 15:
                rec = 'initial calculation still not finished.\n'
                rec += '---'*25
                record(submitted_jobs[0].root_path, rec)
                r = 0

    # submit and detect the other jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
            if count < max_paralell and len(jobs) != 0:
                new_job = jobs.pop()
                os.chdir(new_job.path)
                nearest_job = obtain_nearest_job(new_job)
                rename_file(new_job.path, 'hf.out')
                rename_file(new_job.path, 'fort.9')
                # copy_fort9(new_job)
                copy_submit_scr(new_job, nodes, crystal_path, nearest_job)
                out = submit_job(new_job, 'hf')
                count += 1
                submitted_jobs.append(new_job)
                rec = str(new_job) + '\n'
                rec += 'job submitted.'
                rec += '\n' + out + '\n'
                rec += '---'*25
                record(new_job.root_path, rec)
                print(rec)
            else:
                # time.sleep(10)
                time.sleep(500)
                j += 1
                test_calculation(j, jobs, submitted_jobs, finished_jobs)    # test function
                if j > 15:
                    rec = 'noting changes.\n'
                    rec += '---'*25
                    record(submitted_jobs[0].root_path, rec)
                    j = 0
                continue

    return finished_jobs


def obtain_nearest_job(curr_job):
    """
    This function is used for choosing the nearest finished job to the current job, which will be used for GUESSP strategy
    :param curr_job:
    :param finished_jobs:
    :return:
    """
    finished_jobs = get_finished_jobs(curr_job)
    nearest_job = 0
    if len(finished_jobs) > 0:
        delta_z = 10000
        for j in finished_jobs:
            if j.x == curr_job.x:
                if 0 < abs(float(j.z) - float(curr_job.z)) < delta_z:
                    delta_z = abs(float(j.z) - float(curr_job.z))
                    nearest_job = j
        if not isinstance(nearest_job, Job):
            distance = 100000
            for j in finished_jobs:
                dis = math.sqrt((float(j.z)-float(curr_job.z))**2 + (float(j.x)-float(curr_job.x))**2)
                if 0 < dis < distance:
                    distance = dis
                    nearest_job = j
    return nearest_job


def get_finished_jobs(job):
    path = os.path.join(job.root_path, job.method)
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if ('hf.out' in files) and ('fort.9' in files):
            new_path = root
            new_job = Job(new_path)
            if if_cal_finish(new_job):
                jobs.append(new_job)
    return jobs


def test_calculation(j, init_jobs, submitted_jobs, finished_jobs):
    # ----------------------------------------- test ---------------------------------------------------
    if j >= 2:
        # categorization of out jobs
        path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\hf1'
        walks = os.walk(path)
        jobs = []
        for root, dirs, files in walks:
            if 'hf.out' in files:
                if 'BS2' not in root:
                    job = Job(root)
                    jobs.append(job)
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
                    fort_from = os.path.join(out_from, 'fort.9')
                    out_from = os.path.join(out_from, 'hf.out')
                    out_to = job_list[i].path
                    fort_to = os.path.join(out_to, 'fort.9')
                    out_to = os.path.join(out_to, 'hf.out')
                    shutil.copy(out_from, out_to)
                    shutil.copy(fort_from, fort_to)
    # ----------------------------------------- test ---------------------------------------------------


if __name__ == '__main__':
    test_calculation(1,1,1)
