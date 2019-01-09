#!/usr/bin/python3
import os
import re
import xlwt
import xlrd
from xlutils.copy import copy
from HF2 import submit_job_hf2
from Common.job_path import Job_path


def get_energy(path):
    f = open(path + '/hf.out', 'r')
    lines = f.read()
    #lines = ' '.join(lines.split()) + '#'
    f.close()

    regex = 'CYC   0.*?\n'
    energy_block = re.search(regex, lines).group(0)    # CYC   0 ETOT(AU) -2.726040216969E+03 DETOT -2.73E+03 tst  0.00E+00 PX  1.00E+00
    regex_2 = 'ETOT\(AU\) .*? '
    energy_block = re.search(regex_2, energy_block).group(0)    #ETOT(AU) -2.726040216969E+03
    energy_block = energy_block.strip()
    energy_block =energy_block.split(' ')
    energy = energy_block[-1]   #str

    return energy


def test_get_energy():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106'
    energy = get_energy(path)
    expected = '-2.726040216969E+03'
    assert(energy == expected)


def get_init_distance(job):
    path = job.root_path
    path = os.path.join(path, 'geo_opt')
    path = os.path.join(path, 'init_distance')
    with open(path, 'r') as f:
        init_dist = f.read()
    init_dist = init_dist.strip()
    init_dist = float(init_dist)
    return init_dist

def test_get_init_distance():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106'
    job = Job_path(path)
    init_dist = get_init_distance(job)
    expected = 3.1
    assert(init_dist == expected)


def get_all_abs_x_z(jobs, init_distance):
    x_set = set()
    z_set = set()
    for job in jobs:
        x = job.get_x_value()
        x_set.add(x)
        z = job.get_z_value()
        z_set.add(z)
    x_list = list(x_set)
    z_list = list(z_set)
    x_list.sort()
    z_list.sort()
    for i in range(len(z_list)):
        z_list[i] = z_list[i] + init_distance
    x_dict = {}
    z_dict = {}
    for i in range(len(x_list)):
        x_dict[x_list[i]] = i
    for i in range(len(z_list)):
        z_dict[z_list[i]] = i
    return x_dict, z_dict

def test_get_all_x_z():
    paths = [r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106', r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106\underlayer', r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106\upperlayer']
    jobs = [Job_path(path) for path in paths]
    x_dict, z_dict = get_all_abs_x_z(jobs, 3.1)
    x_expected = {-0.15: 0}
    z_expected = {2.994: 0}
    assert(x_expected == x_dict)
    assert(z_expected == z_dict)


def creatxls_dis(path):
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('hf2')   #creat new sheet
    ws.write(0, 0, 'displacement')
    ws.write(0, 1, 'distance(A)')
    ws.write(0, 2, 'E(au)')
    ws.write(0, 3, 'Eupperlayer(au)')
    ws.write(0, 4, 'Eunderlayer(au)')
    ws.write(0, 5, 'deltaE')
    wb.save(path + '/hf2.xls')  #save the sheet


def data_saving_dis(i, path, disp, dis, l, energy):
    try:
        file = path + '/hf2.xls'
        rb = xlrd.open_workbook(file, formatting_info=True)
        wb = copy(rb)
        ws = wb.get_sheet(0)
        ws.write(i, 0, str(disp))
        ws.write(i, 1, str(dis))
        ws.write(i, l, str(energy))
        wb.save(path + '/hf2.xls')
    except Exception as e:
        print(e)


def read_and_record_result(job, init_distance, x_dict, z_dict):
    path = job.path
    energy = get_energy(path)
    path = job.root_path
    z = job.get_z_value() + init_distance
    x = job.get_x_value()
    j = 1 + len(x_dict) * z_dict[z] + x_dict[x]
    layer = {'bilayer': 2, 'upperlayer': 3, 'underlayer': 4}
    l = layer[job.layertype]
    data_saving_dis(j, path, x, z, l, energy)


def read_all_results(job_dirs, init_distance = 3.1):
    finished_path = []
    readed_path = []

    #get the initial distance of the system
    try:
        init_distance = get_init_distance(job_dirs[0])
    except Exception as e:
        print(e)
        init_distance = None
    if init_distance == None:
        init_distance = get_layer_distance(job_dirs[0])
    x_dict, z_dict = get_all_abs_x_z(job_dirs, init_distance)

    #pick up the initial system
    loc = 0
    for job in job_dirs:
        if job.layertype == 'bilayer' and job.get_x_value() == 0 and job.get_z_value == init_distance:
            break
        loc += 1

    creatxls_dis(job_dirs[0].root_path)

    def test_finished(paths):
        """
        test one job is finished or not,
        if finished, add the path to list finished_path, and delete it from the original list
        :param paths:
        :return:
        """
        for path in paths:
            if submit_job_hf2.if_cal_finish(path):
                finished_path.append(path)
                paths.remove(path)
            else:
                pass

    i = 0
    length = len(job_dirs)
    while i < length:
        test_finished(job_dirs)
        if len(finished_path) > i:
            read_and_record_result(finished_path[i], init_distance, x_dict, z_dict)
            readed_path.append(finished_path[i])
            i += 1
        else:
            time.sleep(500)
            continue


def test_read_all_results():
    paths = [r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106', r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106\underlayer', r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106\upperlayer']
    jobs = [Job_path(path) for path in paths]
    read_all_results(jobs)


def test_suite():
    test_get_energy()
    test_get_init_distance()
    test_get_all_x_z()
    test_read_all_results()

#test_suite()


