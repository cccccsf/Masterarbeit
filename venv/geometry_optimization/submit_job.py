#!/usr/bin/python3
import os
import re
import subprocess
import shutil
import time

def submit_job_without_displacement():
    command = 'qsub job_submit_without_displacement.bash'
    subprocess.call(command, shell=True)


def submit_job_with_displacement():
    command = 'qsub job_submit_with_displacement.bash'
    subprocess.call(command, shell=True)


def submit_geo_opt_job():
    chmod = 'chmod u+x geo_opt.bash'
    command = 'qsub geo_opt.bash'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)


def copy_submit_scr(path, dirname, init = 0):
    #path = os.path.join(path, '/geo_opt', dirname)
    path = path + '/geo_opt/' + dirname
    if init == 1:
        scr_path = os.path.dirname(os.path.realpath(__file__)) + '/../geometry_optimization/job_submit_without_displacement.bash'
    else:
        scr_path = os.path.dirname(os.path.realpath(__file__)) + '/../geometry_optimization/job_submit_with_displacement.bash'
    shutil.copy(scr_path, path+'/geo_opt.bash')
    print('Submition file copied...')


def get_job_dirs(path):
    path = path + '/geo_opt/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'geo_opt.bash' in files:
            job_dirs.append(root)
    return job_dirs

def if_cal_finish(path):
    """
    check the calculation is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    os.chdir(path)
    if not os.path.exists('geo_opt.out'):
        return False
    else:
        file = open('geo_opt.out', 'r')
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


def if_init_finished(path):
    z_dirname = os.path.split(path)[-1]
    superior_path = os.path.split(path)[0]
    x_dirname = os.path.split(superior_path)[-1]
    root_path = os.path.split(superior_path)[0]
    x = float(x_dirname.split('_')[-1])
    if x == 0:
        return True
    init_path = root_path + '/x_0/' + z_dirname
    if not if_cal_finish(init_path):
        return False
    file = os.path.exists(init_path+'/fort.9')
    if not file:
        return False
    return True

def submit(job_dirs):
    max_paralell = 5
    count = 0
    submitted_path = []
    finished_path = []

    def test_finished(paths):
        for path in paths:
            if if_cal_finish(path):
                finished_path.append(path)
                print(path)
                print('calculation finished..')
                paths.remove(path)
                count -= 1
            else:
                pass
    i = 0
    while i < len(job_dirs):
        test_finished(submitted_path)
        if count <= max_paralell:
            os.chdir(job_dirs[i])
            if not os.path.exists('geo_opt.bash'):
                print('wrong path:')
                print(job_dirs[i])
            else:
                #submit_geo_opt_job()
                if if_init_finished(job_dirs[i]):
                    count += 1
                    submitted_path.append(job_dirs[i])
                    i += 1
                else:
                    time.sleep(300)
                    continue
        else:
            time.sleep(500)
            continue

    return finished_path


# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_0\\z_0'
# aa = if_cal_finish(path)
# print(aa)
