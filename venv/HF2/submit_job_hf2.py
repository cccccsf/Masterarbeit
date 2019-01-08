#!/usr/bin/python3
import os
import subprocess
import shutil
import time


def submit_hf2_job():
    chmod = 'chmod u+x hf2'
    command = 'qsub hf2'
    subprocess.call(chmod, shell=True)
    subprocess.call(command, shell=True)



def copy_submit_scr(path):
    ziel_path = path.path.replace('hf_1', 'hf_2')
    scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit.bash'
    try:
        print(ziel_path)
        shutil.copy(scr_path, ziel_path+'/hf.bash')
        print('Submition file copied...')
    except Exception as e:
        print(e)


def copy_fort9(path):
    scr_path = path.path + '/fort.9'
    ziel_path = path.path.replace('hf_1', 'hf_2')
    try:
        print(ziel_path)
        shutil.copy(scr_path, ziel_path+'/fort.9')
        print('fort.9 copied...')
    except Exception as e:
        print(e)


def if_cal_finish(path):
    """
    check the calculation is finished or not through the output file
    :param path: string
    :return: Bool Ture of False
    """
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


def if_init_finished(path):
    if path.layertype != 'upperlayer' and path.layertype != 'underlayer':
        x = path.get_x_value()
        if x == 0:
            return True
        init_path = path.root_path + '/x_0/' + path.z_dirname
        if not if_cal_finish(init_path):
            return False
        file = os.path.exists(init_path+'/fort.9')
        if not file:
            return False
        return True
    else:
        x = path.get_x_value()
        if x == 0:
            return True
        init_path = path.root_path + '/x_0/' + path.z_dirname + '/' + self.layertype
        if not if_cal_finish(init_path):
            return False
        file = os.path.exists(init_path+'/fort.9')
        if not file:
            return False
        return True

def get_job_dirs(path):
    path = path + '/hf_2/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'hf2' in files:
            job_dirs.append(root)
    return job_dirs


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
            os.chdir(job_dirs[i].path)
            if not os.path.exists('hf2.bash'):
                print('wrong path:')
                print(job_dirs[i].path)
            else:
                #submit_hf2_job()
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


#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\hf_1\\x_-0.150\\z_-0.106\\upperlayer'
#copy_submit_scr(path)
#copy_fort9(path)

