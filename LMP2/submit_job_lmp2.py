#!/usr/bin/python3
import os
import re
import shutil
import time
from Common import record
<<<<<<< HEAD


def submit_lmp2_job():
    chmod = 'chmod u+x lmp2'
    subprocess.call(chmod, shell=True)
    try:
        out_bytes = subprocess.check_output(['qsub', 'lmp2'])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    #print('job submitted...')
    #print(out_text)
    return out_text
=======
from Common import submit_job
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad


def copy_fort80(ziel_path):
    original_path = ziel_path.replace('lmp2', 'hf1')
    try:
        fort80_to = os.path.join(ziel_path, 'fort.80')
        fort80_from = os.path.join(original_path, 'fort.80')
        shutil.copy(fort80_from, fort80_to)
        print('fort.80 copied.')
    except Exception as e:
        print(e)
        print('fort.80 failed to copy.')


def copy_fort9_fort78(ziel_path):
    original_path = ziel_path.replace('lmp2', 'hf2')
    try:
        fort9_from = os.path.join(original_path, 'fort.9')
        fort9_to = os.path.join(ziel_path, 'fort.9')
        fort78_from = os.path.join(original_path, 'fort.78')
        fort78_to = os.path.join(ziel_path, 'fort.78')
        shutil.copy(fort9_from, fort9_to)
        shutil.copy(fort78_from, fort78_to)
        print('fort.9 and fort.78 copied.')
    except Exception as e:
        print(e)
        print('fort.9 and fort.78 failed to copy.')


def copy_submit_src(job, ziel_path, nodes, cryscor_path):
    scr_path = os.path.dirname(__file__)
    scr_from = os.path.join(scr_path, 'job_submit_lmp2.bash')
    scr_to = os.path.join(ziel_path, 'lmp2')
    try:
        shutil.copy(scr_from, scr_to)
        update_scr(job, ziel_path, nodes, cryscor_path)
        insert_path_fort(job)
        print('Submition file copied.')
    except Exception as e:
        print(e)
        print('submit scr failed to copy.')


def update_scr(job, path, nodes, cryscor_path):
    scr = os.path.join(path, 'lmp2')
    with open(scr, 'r') as f:
        lines = f.readlines()

    # update nodes
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
    if nodes != '' and nodes != 'default':
        nodes_line = '#PBS -l nodes={}'.format(nodes)
        lines[loc] = nodes_line

    # update cryscor path and currdir
    loc_cry, loc_curr, i = 0, 0, 0
    for line in lines:
        if line.startswith('cryscor_path'):
            cryscor_line = line
            loc_cry = i
        if line.startswith('currdir='):
            currdir_line = line
            loc_curr = i
        i += 1
    if cryscor_path != '':
        cryscor_line = 'cryscor_path={}\n'.format(cryscor_path)
        lines[loc_cry] = cryscor_line
    if job.layertype == 'bilayer':
        currdir_line = 'currdir=/scratch/$USER/lmp2/{}/{}\n'.format(job.x_dirname, job.z_dirname)
    else:
        currdir_line = 'currdir=/scratch/$USER/lmp2/{}/{}/{}\n'.format(job.x_dirname, job.z_dirname, job.layertype)
    lines[loc_curr] = currdir_line

    with open(scr, 'w') as f:
        f.writelines(lines)


def insert_path_fort(job):
    submit_file = os.path.join(job.path, 'lmp2')
    with open(submit_file, 'r') as f:
        lines = f.readlines()
    # fort.9
    fort9, fort78, fort80 = 0, 0, 0
    for i in range(len(lines)):
        if lines[i].startswith('cp fort.9'):
            fort9 = i
        elif lines[i].startswith('cp fort.78'):
            fort78 = i
        elif lines[i].startswith('cp fort.80'):
            fort80 = i
    fort9_path = os.path.join(job.path.replace('lmp2', 'hf2'), 'fort.9')
    fort78_path = os.path.join(job.path.replace('lmp2', 'hf2'), 'fort.78')
    fort80_path = os.path.join(job.path.replace('lmp2', 'hf1'), 'fort.80')
    lines[fort9] = lines[fort9].replace('fort.9', fort9_path)
    lines[fort78] = lines[fort78].replace('fort.78', fort78_path)
    lines[fort80] = lines[fort80].replace('fort.80', fort80_path)
    with open(submit_file, 'w') as f:
        f.writelines(lines)


def copy_files(job, nodes, cryscor_path):
    ziel_path = job.path
    copy_submit_src(job, ziel_path, nodes, cryscor_path)
    # copy_fort80(ziel_path)
    # copy_fort9_fort78(ziel_path)


def if_cal_finish(job):
    path = job.path
    out_path = os.path.join(path, 'lmp2.out')
    if not os.path.exists(out_path):
        return False
    else:
        with open(out_path, 'rb') as f:
            f.seek(-1000, 2)
            out = f.read().decode('utf-8')
        regex = 'TERMINATION  DATE'
        termination = re.search(regex, out)
        if termination is None:
            return False
        else:
            if termination.group(0) != 'TERMINATION  DATE':
                return False
            else:
                return True


def submit(jobs):
    job_num = len(jobs)
    max_paralell = 8
    # max_paralell = 75
    count = 0
    submitted_jobs = []
    finished_jobs = []

    def test_finished(jobs):
        """
        test jobs which have benn submittdt is finished or not
        if a job finished, add it to list finished_jobs, and delete it from list submitted_jobs
        :param jobs:
        :return:
        """
        nonlocal count
        for job in jobs[:]:
            if if_cal_finish(job):
                finished_jobs.append(job)
<<<<<<< HEAD
                num = str(len(finished_jobs)) + '/' + str(jobs_num)
                rec = job.path
                rec += '\n'
                rec += num
                rec += ' calculation finished...'
=======
                num = str(len(finished_jobs)) + '/' + str(job_num)
                rec = str(job)
                rec += '\n'
                rec += num + '  calculation finished.\n'
                rec += '---'*25
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
                print(rec)
                record(job.root_path, rec)
                jobs.remove(job)
                count -= 1

    # test if there is some job which is already finished
    for job in jobs[:]:
        if if_cal_finish(job):
            finished_jobs.append(job)
            jobs.remove(job)

    # submit and detect all jobs
    j = 0
    while True:
        test_finished(submitted_jobs)   # update list finished_jobs and list submitted_jobs
        if len(finished_jobs) == job_num and len(submitted_jobs) == 0:
            break
        else:
<<<<<<< HEAD
            if count <= max_paralell and len(jobs) != 0:       #check the number of jobs which is running now
=======
            if count <= max_paralell and len(jobs) > 0:       # check the number of jobs which is running now
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
                new_job = jobs.pop()
                os.chdir(new_job.path)
                out = submit_job(new_job, 'lmp2')
                count += 1
                submitted_jobs.append(new_job)
                rec = str(new_job) + '\n'
                rec += 'job submitted.'
                rec += '\n' + out + '\n'
                rec += '---'*25
                record(new_job.root_path, rec)
                print(rec)
            else:
                time.sleep(500)
                # time.sleep(1)
                j += 1
                test_calculation(j, jobs, submitted_jobs, finished_jobs)    # test function
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
        from Common import Job
        # categorization of out jobs
        path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\lmp2'
        walks = os.walk(path)
        jobs = []
        for root, dirs, files in walks:
            if 'lmp2.out' in files:
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
                    out_from = os.path.join(out_from, 'lmp2.out')
                    out_to = job_list[i].path
                    out_to = os.path.join(out_to, 'lmp2.out')
                    shutil.copy(out_from, out_to)
    # ----------------------------------------- test ---------------------------------------------------


if __name__ == '__main__':
    test_calculation(3,1,1,1)
