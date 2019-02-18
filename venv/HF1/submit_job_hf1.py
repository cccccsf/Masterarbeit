#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time
from Common import record



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


def copy_submit_scr(job, nodes, crystal_path):
    ziel_path = job.path
    scr_path = os.path.dirname(os.path.realpath(__file__))
    if job.x == '0' and job.z == '0':
        scr_from = os.path.join(scr_path, 'job_submit_init.bash')
    else:
        scr_from = os.path.join(scr_path, 'job_submit.bash')
    scr_to = os.path.join(ziel_path, 'hf')
    shutil.copy(scr_from, scr_to)
    update_nodes(ziel_path, nodes, crystal_path)
    print('Submition file copied...')


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
                nodes_line = line
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
        lines[loc2] = 'mpirun -np {} $crystal_path/Pcrystal >& ${{PBS_O_WORKDIR}}/geo_opt.out\n'.format(nodes)
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
    :param path: string
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
            if line == None:
                return False
            else:
                if line.group(0) != 'TOTAL CPU TIME':
                    return False
                else:
                    return True
        return True
    except FileNotFoundError as e:
        return False


def submit(jobs):
    job_num = len(jobs)
    max_paralell = 5
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

    #find and submit the initial job
    init_jobs = []
    for job in jobs:
        if job.x == '0':
            print(job.x, job.z, job.layertype)
            init_jobs.append(job)
            jobs.remove(job)
    for job in init_jobs:
        if not if_cal_finish(job):
            os.chdir(job.path)
            #out = submit_hf1_job()
            out = '0000'
            count += 1
            submitted_jobs.append(job)
            rec = job.path
            print(rec)
            rec += '\n'
            rec += 'job submitted...'
            rec += '\n' + out
            record(job.root_path, rec)
        else:
            finished_jobs.append(job)
    #detect if init jobs finished
    r = 0
    while True:
        test_finished(submitted_jobs)
        if len(submitted_jobs) == 0:
            break
        else:
            time.sleep(500)
            r += 1
            if r > 15:
                rec = job_init.path
                rec += '\n'
                rec += 'initial calculation still not finished...'
                record(submitted_jobs[0].root_path, rec)
                r = 0

    #submit and detect the other jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
            if count < max_paralell:
                new_job = jobs.pop()
                print(new_job)
                os.chdir(new_job.path)
                copy_fort9(new_job)
                out = submit_hf1_job()
                count += 1
                submitted_jobs.append(new_job)
                rec = new_job.path + '\n'
                rec += 'job submitted...'
                rec += '\n' + out
                record(new_job.root_path, rec)
            else:
                time.sleep(500)
                j += 1
                if j > 15:
                    rec += 'noting changes...'
                    record(submitted_jobs[0].root_path, rec)
                    j = 0
                continue

    return finished_jobs
