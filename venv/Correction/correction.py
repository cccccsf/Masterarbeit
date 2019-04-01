#!/usr/bin/python3
import os
import re
import sys
from copy import deepcopy
from Common import record
from Common import ReadIni
from Common import Job_path
import Correction
from HF1 import read_init_dis


yes_or_no = {
    'Y': 1,
    'y': 1,
    'Yes': 1,
    'yes': 1,
    'N': 0,
    'n': 0,
    'No': 0,
    'no': 0}


def correction(path):

    rec = 'Correction Calculation begins...'
    print(rec)
    record(path, rec)

    # get jobs
    cluster_jobs = get_jobs(path)

    # read info from ini file
    init_dist = read_init_dis(path)
    ini_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    ini_file = os.path.exists(os.path.join(ini_path, 'input.ini'))
    if ini_file:
        Ini = ReadIni(ini_path)
        molpro_path, molpro_key, nodes, memorys = Ini.read_correction_info()
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    # prepare input
    cluster_path = os.path.join(path, 'cluster')
    missions, nodes, memorys = get_missions(memorys, nodes)

    inputs = list(missions)
    inputs = [inp + '.inp' for inp in inputs]
    inputs_files = [os.path.join(cluster_path, inp) for inp in inputs]

    while True:
        if check_inp_files(inputs_files):
            break
        if not check_inp_files(inputs_files):
            print('Please finish different input files in the following path: ')
            print(cluster_path)
            print('And name them as following:')
            for i in inputs:
                print(i)
            print('Then press ENTER to continue the programm.')
            then = input()
    inputs, nodes, memorys = compare_inp_files(
        cluster_path, inputs, nodes, memorys)
    inputs_dict = {
        inp.split('.')[0]: os.path.join(
            cluster_path,
            inp) for inp in inputs}
    inputs = [inp.split('.')[0] for inp in inputs]

    # generation input
    correction_jobs = []
    correction_jobs_dict = {inp: [] for inp in inputs}
    for job in cluster_jobs:
        xyz_name = ''
        for inp in inputs:
            new_job = deepcopy(job)
            new_job.method = inp
            new_job.parameter['node'] = nodes[inp]
            new_job.parameter['memory'] = memorys[inp]
            new_job.parameter['original_input_file'] = inputs_dict[inp]
            correction_jobs.append(new_job)
            correction_jobs_dict[inp].append(new_job)
            if xyz_name == '':
                xyz_name = Correction.generation_input(new_job)
            else:
                Correction.generation_input(new_job, xyz_name)
    # deal with the one with periodic bs
    per = ''
    for i in inputs:
        if i.startswith('per'):
            per = i
            break
    if per == '':
        print('Job with the basis set for periodic system not found.')
        print('Please enter the name of input file '
              'or enter 1 to pass this calculation'
              'or enter 0 to exit the programm.')
        while True:
            per_st = input()
            if per_st == 0:
                sys.exit()
                print('Programm exit...')
            elif per_st == 1:
                break
            else:
                if per_st in inputs:
                    per = per_st
                    break
                else:
                    print('Please enter the correct name of input file with suffix.')
    if per != '':
        per_jobs = correction_jobs_dict[per]
        inp_name = per + '.inp'
        for job in per_jobs:
            MB = Correction.Molpro_Bs(job, inp_name)
            MB.get_molpro_bs()
            MB.write_bs()

    # generate scr
    for key, value in correction_jobs_dict.items():
        for job in value:
            Scr = Correction.Script(job, molpro_key, molpro_path)
            Scr.write_scr()

    # submit jobs
    jobs_finished = correction_jobs  # only for test
    #jobs_finished = Correction.submit(correction_jobs)

    # read and record all results
    if len(jobs_finished) != 0:
        Correction.read_all_results(jobs_finished, init_distance=init_dist)

    print('Correction calculation finished!!!')
    record(path, 'Correction calculation finished!!!')


def get_missions(memorys, nodes):
    missions_nodes = {key for key in nodes.keys()}
    missions_memory = {key for key in memorys.keys()}
    missions = missions_memory | missions_nodes
    for m in missions:
        if m not in missions_nodes:
            print('nodes info of job {} not found!'.format(m))
            print('Do you want to use the default value 12? Please enter y(es)/n(o)...')
            default = input()
            default = yes_or_no[default]
            if default == 1:
                nodes[m] = 12
            else:
                print('Please correct the info and restart the programm.')
                print('Programm exits...')
                sys.exit()
        if m not in missions_memory:
            print('memory info of job {} not found!'.format(m))
            print(
                'Do you want to use the default value 2000 M ? Please enter y(es)/n(o)...')
            default = input()
            default = yes_or_no[default]
            if default == 1:
                memorys[m] = 2000
            else:
                print('Please correct the info and restart the programm.')
                print('Programm exits...')
                sys.exit()
    return missions, nodes, memorys


def get_jobs(path):
    path = os.path.join(path, 'cluster')
    walks = os.walk(path)
    jobs = []
    path_set = set()
    for root, dirs, files in walks:
        if len(files) > 0:
            for file in files:
                if os.path.splitext(
                        file)[-1] == '.xyz' and root not in path_set:
                    path_set.add(root)
                    new_job = Job_path(root)
                    jobs.append(new_job)
    return jobs


def compare_inp_files(path, inputs, nodes, memorys):
    walks = os.walk(path)
    for root, dirs, files in walks:
        if root == path:
            f = files
    files = [i for i in f if i.endswith('.inp')]
    for f in files:
        if f not in inputs:
            print(f, ';  job info not include in ini file.')
            print('Do you want to use default setting to calculate?')
            print('Please enter y(es)/n(o)...')
            default = input()
            #default = 'y'
            default = yes_or_no[default]
            if default == 1:
                nodes[f.split('.')[0]] = 12
                memorys[f.split('.')[0]] = 2000
            else:
                print(
                    'Please add the info in ini file or delete needless input file and restart the programm.')
                print('Programm exits...')
                sys.exit()
    return inputs, nodes, memorys


def check_inp_files(inputs_files):
    for inp in inputs_files:
        if not os.path.exists(inp):
            return False
    return True
