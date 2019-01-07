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


def get_x_z_and_layertype(path):
    z = os.path.split(path)[-1]
    path = os.path.split(path)[0]
    layertype = 'bilayer'
    if z == 'underlayer' or z =='upperlayer':
        layertype = z
        z = os.path.split(path)[-1]
        path  = os.path.split(path)[0]
    z_dir = z
    z = float(z.split('_')[-1])
    x = os.path.split(path)[-1]
    x_dir = x
    root_path = os.path.split(path)[0]
    x = float(x.split('_')[-1])
    root_path = os.path.split(root_path)[0]
    return x_dir, z_dir, layertype, root_path


def copy_submit_scr(path):
    x_dir, z_dir, layertype, root_path = get_x_z_and_layertype(path)
    if layertype == 'bilayer':
        ziel_path = root_path + '/hf_2/' + x_dir + '/' + z_dir
    else:
        ziel_path = root_path + '/hf_2/' + x_dir + '/' + z_dir + '/' + layertype
    scr_path = os.path.dirname(os.path.realpath(__file__)) + '/job_submit.bash'
    try:
        print(ziel_path)
        shutil.copy(scr_path, ziel_path+'/hf.bash')
        print('Submition file copied...')
    except Exception as e:
        print(e)


def copy_fort9(path):
    x_dir, z_dir, layertype, root_path = get_x_z_and_layertype(path)
    if layertype == 'bilayer':
        ziel_path = root_path + '/hf_2/' + x_dir + '/' + z_dir
    else:
        ziel_path = root_path + '/hf_2/' + x_dir + '/' + z_dir + '/' + layertype
    scr_path = path + '/fort.9'
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


#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\hf_1\\x_-0.150\\z_-0.106\\upperlayer'
#copy_submit_scr(path)
#copy_fort9(path)

