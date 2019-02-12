#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time


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


def update_scr(job, nodes, molpro_key, molpro_path):
    scr = os.path.join(path, 'geo_opt')

    i = 0
    loc_nodes, loc_scratch,
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
        lines[loc2] = 'mpirun -np {} $crystal_path/Pcrystal >& ${PBS_O_WORKDIR}/geo_opt.out\n'.format(nodes)
    if crystal_path != '':
        lines[loc_cry] = 'crystal_path={}\n'.format(crystal_path)

    with open(scr, 'w') as f:
        f.writelines(lines)


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
            return False


def submit(jobs):
    job_num = len(jobs)
    max_paralell = 5
    count = 0
    submitted_jobs = []
    finished_jobs = []

    def test_finished(jobs):
        """
        test jobs which have benn submittdt is finished or not
        if a job finished, add it to list finished_jobs, and delete it from list submitted_jobs
        :param submitted_jobs:
        :return:
        """
        for job in jobs:
            if if_cal_finish(job):
                finished_jobs.append(job)
                print(job)
                print('calculation finished..')
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
                out = submit_rpa_job()
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

