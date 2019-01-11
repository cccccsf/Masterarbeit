#!/usr/bin/python3
import os
import re
import xlwt
import xlrd
from xlutils.copy import copy
from Common.job_path import Job_path
from LMP2.submit_job_lmp2 import if_cal_finish

def get_energy(path):

    path = os.path.join(path, 'lmp2.out')
    with open(path, 'r') as f:
        lines = f.read()
        regex = 'FINAL SUMMARY.*?\*+.*?\*\*+'
    final_summary = re.search(regex, lines, re.M|re.S)
    if final_summary != None:
        final_summary = final_summary.group(0)
    else:
        print(path)
        print('Energy infomation not found...')

    regex = 'MP2 CORRELATION ENERGY.*?\n'
    lmp2 = re.search(regex, final_summary)
    if lmp2 != None:
        lmp2 = lmp2.group(0)
        lmp2 = lmp2.strip()
        lmp2 = lmp2.split()
        lmp2 = lmp2[-2]
    else:
        print(path)
        print('LMP2 erengy not found...')

    regex = 'HF\+SINGLES\+E\(GRIMME\).*?\n'
    scs = re.search(regex, final_summary)
    if scs != None:
        scs = scs.group(0)
        scs = scs.strip()
        scs = scs.split()
        scs = scs[-2]

    return lmp2, scs
"""
                                FINAL SUMMARY

 *******************************************************************************
 *                                                                             *
 *                                          HF ENERGY:   0.0000000000E+00      *
 *                                     SINGLES ENERGY:   0.0000000000E+00      *
 *                             MP2 CORRELATION ENERGY:  -0.6353830194E+00      *
 *                              HF+SINGLES+MP2 ENERGY:  -0.6353830194E+00      *
 *                        HF+SINGLES+E(GRIMME) ENERGY:  -0.6041517836E+00      *
 *                                                                             *
 *******************************************************************************
 """

def get_init_distance(job):
    path = job.root_path
    path = os.path.join(path, 'geo_opt')
    path = os.path.join(path, 'init_distance')
    with open(path, 'r') as f:
        init_dist = f.read()
    init_dist = init_dist.strip()
    init_dist = float(init_dist)
    return init_dist


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


def creatxls_dis(path, type):
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet(type)   #creat new sheet
    ws.write(0, 0, 'displacement')
    ws.write(0, 1, 'distance(A)')
    ws.write(0, 2, 'E(au)')
    ws.write(0, 3, 'Eupperlayer(au)')
    ws.write(0, 4, 'Eunderlayer(au)')
    ws.write(0, 5, 'deltaE')
    wb.save(path + '/{}.xls'.format(type))  #save the sheet


def data_saving_dis(i, path, disp, dis, l, energy, type):
    try:
        file = path + '/{}.xls'.format(type)
        rb = xlrd.open_workbook(file, formatting_info=True)
        wb = copy(rb)
        ws = wb.get_sheet(0)
        ws.write(i, 0, str(disp))
        ws.write(i, 1, str(dis))
        ws.write(i, l, str(energy))
        wb.save(path + '/{}.xls'.format(type))
    except Exception as e:
        print(e)


def read_and_record_result(job, init_distance, x_dict, z_dict):
    path = job.path
    Elmp2, Escs_lmp2 = get_energy(path)
    path = job.root_path
    z = job.get_z_value() + init_distance
    x = job.get_x_value()
    j = 1 + len(x_dict) * z_dict[z] + x_dict[x]
    layer = {'bilayer': 2, 'upperlayer': 3, 'underlayer': 4}
    l = layer[job.layertype]
    data_saving_dis(j, path, x, z, l, Elmp2, 'lmp2')
    data_saving_dis(j, path, x, z, l, Escs_lmp2, 'scs_lmp2')


def read_all_results(jobs, init_distance = None):
    readed_jobs = []

    #get the initial distance of the system
    try:
        init_distance = get_init_distance(jobs[0])
    except Exception as e:
        print(e)
        init_distance = None
    if init_distance == None:
        while True:
            try:
                print('Please enter the initial layer distance of the system:')
                init_distance = input()
                init_distance = float(init_distance)
                break
            except Exception as e:
                print(e)
                print('Please enter the right number of the initial layer distance!!!')
    x_dict, z_dict = get_all_abs_x_z(jobs, init_distance)

    creatxls_dis(jobs[0].root_path, 'lmp2')
    creatxls_dis(jobs[0].root_path, 'scs_lmp2')

    for i in range(len(jobs)):
        read_and_record_result(jobs[i], init_distance, x_dict, z_dict)
        readed_jobs.append(jobs[i])

