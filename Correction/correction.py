#!/usr/bin/python3
import os
import sys
from copy import deepcopy
from Common import record
from Common import ReadIni
from Common import record_data_json
from Common import Job
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

    rec = 'Correction begins.\n'
    rec += '---'*25
    print(rec)
    record(path, rec)

    # get jobs
    cluster_jobs = get_jobs(path)
    init_dist = read_init_dis(path)

    # read infos from input.ini file
    Ini = ReadIni()
    project_name, *_ = Ini.get_basic_info()
    nodes, memorys, bs, molpro_path, molpro_key, atoms = Ini.get_correction()
    record_data_json(path, 'memorys', memorys, section='correction')
    record_data_json(path, 'nodes', nodes, section='correction')

    # prepare input
    cluster_path = os.path.join(path, 'cluster')
    missions, nodes, memorys = get_missions(memorys, nodes)

    inputs = list(missions)
    inputs = [inp + '.inp' for inp in inputs]
    inputs_files = [os.path.join(cluster_path, inp) for inp in inputs]

    inputs, nodes, memorys = compare_inp_files(
        cluster_path, inputs, nodes, memorys)
    inputs_dict = {
        inp.split('.')[0]: os.path.join(
            cluster_path,
            inp) for inp in inputs}     # input file maybe exists in \cluster\ directory
    inputs = [inp.split('.')[0] for inp in inputs]

    # generation input
    correction_jobs = []
    correction_jobs_finished = []
    correction_jobs_dict = {inp: [] for inp in inputs}
    for job in cluster_jobs:
        for inp in inputs:
            new_job = deepcopy(job)
            new_job.method = inp
            new_job.parameter['node'] = nodes[inp]
            new_job.parameter['memory'] = memorys[inp]
            new_job.parameter['original_input_file'] = inputs_dict[inp]
            if not Correction.if_cal_finish(new_job):
                if not os.path.exists(inputs_dict[inp]):
                    print(str(new_job))
                    print('{} file not found.'.format(inp))
                    print('Program will generate the input automatically.')
                    print('---'*25)
                    if new_job.method.startswith('per'):
                        Inp = Correction.InputPerRPA(new_job, project_name, memorys[new_job.method], uc_atoms=atoms)
                        Inp.gen_inp()
                    elif new_job.method.endswith('rpa_cc'):
                        Inp = Correction.InputRPACC(new_job, project_name, memorys[new_job.method], uc_atoms=atoms)
                        Inp.gen_inp()
                    elif new_job.method.endswith('iext1_rpa'):
                        Inp = Correction.InputIext1RPA(new_job, project_name, memorys[new_job.method], uc_atoms=atoms)
                        Inp.gen_inp()
                else:
                    if new_job.method.startswith('per'):
                        inp_name = new_job.method + '.inp'
                        MB = Correction.Molpro_Bs(new_job, inp_name)
                        MB.get_molpro_bs()
                        MB.write_bs()
                    else:
                        Correction.generation_input(new_job)
                correction_jobs.append(new_job)
                correction_jobs_dict[inp].append(new_job)
            else:
                new_job.status = 'finished'
                correction_jobs_finished.append(new_job)

    # generate scr
    for key, value in correction_jobs_dict.items():
        for job in value:
            Scr = Correction.Script(job, molpro_key, molpro_path)
            Scr.write_scr()

    # submit jobs
    if len(correction_jobs) > 0:
        new_finished_jobs = Correction.submit(correction_jobs)
        correction_jobs_finished += new_finished_jobs
    # read and record all results
    if len(correction_jobs_finished) != 0:
        Correction.read_all_results(correction_jobs_finished, init_distance=init_dist)

    rec = 'Correction finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)


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
                    new_job = Job(root)
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
