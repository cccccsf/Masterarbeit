#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time
from Common import record


def submit_hf2_job():
    chmod = 'chmod u+x hf2'
    subprocess.call(chmod, shell=True)
    try:
        out_bytes = subprocess.check_output(['qsub', 'hf2'])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    print('job submitted...')
    print(out_text)
    return out_text


def copy_submit_scr(job, nodes):
    ziel_path = job.path
    ziel_path = ziel_path.replace('hf1', 'hf2')
    scr_path = os.path.dirname(__file__)
    scr_from = os.path.join(scr_path, 'job_submit.bash')
    scr_to = os.path.join(ziel_path, 'hf2')
    try:
        shutil.copy(scr_from, scr_to)
        if nodes != '':
            nodes = int(nodes)
            update_nodes(ziel_path, nodes)
        print('Submition file copied...')
    except Exception as e:
        print(e)


def copy_fort9(job):
    ziel_path = job.path
    fort_from = os.path.join(ziel_path, 'fort.9')
    ziel_path = ziel_path.replace('hf1', 'hf2')
    fort_to = os.path.join(ziel_path, 'fort.20')
    try:
        shutil.copy(fort_from, fort_to)
        print('fort.9 copied...')
    except Exception as e:
        print(e)

def update_nodes(path, nodes):
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
                nodes_line = line
                loc = i
            i += 1
    nodes_line = nodes_line.replace('12', str(nodes))
    lines[loc] = nodes_line
    loc2 = 0
    j = 0
    for line in lines:
        if line.startswith('mpirun -np'):
            loc2 = j
        j += 1
    lines[loc2] = lines[loc2].replace('12', str(nodes))
    with open(scr, 'w') as f:
        f.writelines(lines)


def if_cal_finish(job):
    """
    check the calculation is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    path = job.path
    os.chdir(path.path)
    if not os.path.exists('hf.out'):
        return False
    else:
        file = open('hf.out', 'r')
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
    job_num = len(jobs)
    max_paralell = 6
    count = 0
    submitted_jobs = []
    finished_jobs = []

    def test_finished(jobs):
        nonlocal count
        for job in jobs:
            if if_cal_finish(job):
                finished_jobs.append(job)
                rec = job.path
                rec += '\n'
                rec += 'calculation finished...'
                print(rec)
                record(job.root_path, rec)
                jobs.remove(job)
                count -= 1

    #test if there is some job which is already finished
    for job in jobs:
        if if_cal_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)

    #submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
            if count < max_paralell:
                new_job = jobs.pop()
                os.chdir(new_job.path)
                out = submit_hf2_job()
                count += 1
                submitted_jobs.append(new_job)
                rec = new_job.path + '\n'
                rec += 'job submitted...'
                rec += '\n' + out
                record(new_job.root_path, rec)
				print(rec)
            else:
                time.sleep(500)
                j += 1
                if j > 15:
                    rec += 'noting changes...'
                    record(submitted_jobs[0].root_path, rec)
                    j = 0
                continue

    return finished_jobs

