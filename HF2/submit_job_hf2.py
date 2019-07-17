#!/usr/bin/python3
import os
import re
import shutil
import time
from Common import record
from Common import rename_file
from Common import submit_job
from Common import Job


def copy_submit_scr(job, nodes, crystal_path):
    ziel_path = job.path
    ziel_path = ziel_path.replace('hf1', 'hf2')
    scr_path = os.path.dirname(__file__)
    scr_from = os.path.join(scr_path, 'job_submit.bash')
    scr_to = os.path.join(ziel_path, 'hf2')
    try:
        shutil.copy(scr_from, scr_to)
        update_nodes(ziel_path, nodes, crystal_path)
        insert_path_fort(job, scr_to)
        print('Submition file copied.')
    except Exception as e:
        print(e)


def insert_path_fort(job, scr_to):
    with open(scr_to, 'r') as f:
        lines = f.readlines()
    fort20 = 0
    for i in range(len(lines)):
        if lines[i].startswith('cp fort.20'):
            fort20 = i
    fort20_path = os.path.join(job.path, 'fort.9')
    lines[fort20] = lines[fort20].replace('cp fort.20', 'cp '+fort20_path)
    with open(scr_to, 'w') as f:
        f.writelines(lines)


def copy_fort9(job):
    ziel_path = job.path
    fort_from = os.path.join(ziel_path, 'fort.9')
    ziel_path = ziel_path.replace('hf1', 'hf2')
    fort_to = os.path.join(ziel_path, 'fort.20')
    try:
        shutil.copy(fort_from, fort_to)
        print('fort.9 copied.')
    except Exception as e:
        print(e)


def update_nodes(path, nodes, crystal_path):
    scr = os.path.join(path, 'hf2')
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
        lines[loc2] = 'mpirun -np {} $crystal_path/Pcrystal >& ${{PBS_O_WORKDIR}}/hf2.out\n'.format(nodes)
    if crystal_path != '':
        lines[loc_cry] = 'crystal_path={}\n'.format(crystal_path)

    with open(scr, 'w') as f:
        f.writelines(lines)


def if_cal_finish(job):
    """
    check the calculation is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    path = job.path
    out_file = os.path.join(path, 'hf2.out')
    if not os.path.exists(out_file):
        return False
    else:
        file = open(out_file, 'r')
        lines = file.read().replace('\n', ':')
        file.close()
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


def submit(jobs, moni):
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
                jobs.remove(job)
                count -= 1

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

    # submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        moni.update_status()
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
            if count < max_paralell and len(jobs) > 0:
                new_job = jobs.pop()
                os.chdir(new_job.path)
                rename_file(new_job.path, 'hf2.out')
                out = submit_job(new_job, 'hf2')
                count += 1
                submitted_jobs.append(new_job)
                moni.insert_new_job(new_job, out)
                rec = str(new_job) + '\n'
                rec += 'job submitted.'
                rec += '\n' + out + '\n'
                rec += '---'*25
                record(new_job.root_path, rec)
                print(rec)
            else:
                # time.sleep(500)
                time.sleep(200)
                j += 1
                # test_calculation(j, jobs, submitted_jobs, finished_jobs)    # test function
                if j > 15:
                    rec = 'noting changes.\n'
                    rec += '---'*25
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
            if 'hf2.out' in files:
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
                    fort_from = os.path.join(out_from, 'fort.9')
                    fort_78_from = os.path.join(out_from, 'fort.78')
                    out_from = os.path.join(out_from, 'hf2.out')
                    out_to = job_list[i].path
                    fort_to = os.path.join(out_to, 'fort.9')
                    fort_78_to = os.path.join(out_to, 'fort.78')
                    out_to = os.path.join(out_to, 'hf2.out')
                    shutil.copy(out_from, out_to)
                    shutil.copy(fort_from, fort_to)
                    shutil.copy(fort_78_from, fort_78_to)
    # ----------------------------------------- test ---------------------------------------------------


if __name__ == '__main__':
    test_calculation(3,1,1,1)
