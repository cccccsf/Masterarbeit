#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time
from Common import record

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
    print('loc submit scr copied...')


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
                nodes_line = line
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

def copy_all_files(job_dirs):
    try:
        for job_dir in job_dirs:
            copy_loc_scr(job_dir)
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
        if line == None:
            return False
        else:
            return True
    return True


def test_all_loc_finished(job_dirs):
    while True:
        for job_dir in job_dirs:
            if_finished = if_loc_finish(job_dir)
            if if_finished == False:
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
                num = str(len(finished_jobs)) + '/' + str(jobs_len)
                rec = job.path
                rec += '\n'
                rec += num
                rec += ' localization finished...'
                print(rec)
                record(job.root_path, rec)
                jobs.remove(job)
                count -= 1

    #test if there is some job which is already finished
    for job in jobs[:]:
        if if_loc_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)

    #submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)
        if len(finished_jobs) == jobs_len and len(submitted_jobs) == 0:
            break
        else:
            if count <= max_paralell and len(jobs) != 0:
                new_job = jobs.pop()
                os.chdir(new_job.path)
                out = submit_loc_job()
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
