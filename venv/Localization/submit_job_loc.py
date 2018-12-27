#!/usr/bin/python3
import os
import subprocess
import shutil
import time

def submit_loc_job():
    chmod = 'chmod u+x loc_job'
    command = 'qsub loc_job'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)


def copy_loc_submit_file(path):

    scr_path = os.path.dirname(os.path.realpath(__file__)) + '/loc_job'
    shutil.copy(scr_path, path+'/loc_job')
    print(path)
    print('loc submit file copied...')


def copy_all_files(job_dirs):

    try:
        for job_dir in job_dirs:
            copy_loc_submit_file(job_dir)
    except Exception as e:
        print(e)


def get_job_dirs(path):
    path = path + '/hf_1/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'loc_job' in files:
            job_dirs.append(root)
    return job_dirs


def if_loc_finish(path):
    """
    check the localiztion is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    os.chdir(path)
    if not os.path.exists('loc.out'):
        return False
    else:
        with open('loc.out', 'r') as f:
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


def submit(job_dirs):
    max_paralell = 8
    count = 0
    submitted_path = []
    finished_path = []

    def test_finished(paths):
        for path in paths:
            if if_loc_finish(path):
                finished_path.append(path)
                print(path)
                print('localization finished..')
                paths.remove(path)
                count -= 1
            else:
                pass
    i = 0
    while i < len(job_dirs):
        test_finished(submitted_path)
        if count <= max_paralell:
            os.chdir(job_dirs[i])
            if not os.path.exists('hf1.bash'):
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

    return submitted_path
