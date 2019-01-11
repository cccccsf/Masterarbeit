#!/usr/bin/python3
import os
import subprocess
import shutil
import time



def submit_hf1_job():
    chmod = 'chmod u+x hf1.bash'
    command = 'qsub hf1.bash'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)


def copy_submit_scr(path, dirname, init = 0):
    #path = os.path.join(path, '/geo_opt', dirname)
    path = path + '/hf_1/' + dirname
    layer = os.path.split(path)[-1]
    if layer != 'underlayer' and layer != 'upperlayer':
        if init == 1:
            scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_init.bash'
        else:
            scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit.bash'
    elif layer == 'underlayer':
        if init == 1:
            scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_init.bash'
        else:
            scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_underlayer'
    elif layer == 'upperlayer':
        if init == 1:
            scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_init.bash'
        else:
            scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit_upperlayer'
    print(scr_path)
    shutil.copy(scr_path, path+'/hf1.bash')
    print('Submition file copied...')


def get_job_dirs(path):
    path = path + '/hf_1/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'hf1.bash' in files:
            job_dirs.append(root)
    return job_dirs

def if_cal_finish(path):
    """
    check the calculation is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
    os.chdir(path)
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


def if_init_finished(path):
    if os.path.split(path)[-1] != 'upperlayer' and os.path.split(path)[-1] != 'underlayer':
        z_dirname = os.path.split(path)[-1]
        superior_path = os.path.split(path)[0]
        x_dirname = os.path.split(superior_path)[-1]
        root_path = os.path.split(superior_path)[0]
        x = float(x_dir.split('_')[-1])
        if x == 0:
            return True
        init_path = root_path + '/x_0/' + z_dirname
        if not if_cal_finish(init_path):
            return False
        file = os.path.exists(init_path+'/fort.9')
        if not file:
            return False
        return True
    else:
        layer = os.path.split(path)[-1]
        path = os.path.split(path)[0]
        z_dirname = os.path.split(path)[-1]
        superior_path = os.path.split(path)[0]
        x_dirname = os.path.split(superior_path)[-1]
        root_path = os.path.split(superior_path)[0]
        x = float(x_dir.split('_')[-1])
        if x == 0:
            return True
        init_path = root_path + '/x_0/' + z_dirname + '/' + layer
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
            if not os.path.exists('hf1.bash'):
                print('wrong path:')
                print(job_dirs[i])
            else:
                if if_init_finished(job_dirs[i]):
                    #submit_hf1_job()
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
