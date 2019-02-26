#!/usr/bin/python3
import os
from configparser import ConfigParser

def change_parameters(jobs):
    ini_path = jobs[0].root_path
    ini_path = os.path.join(ini_path, 'hf1')
    ini_file = creat_ini_file(ini_path)
    print('---'*15)
    print('Please input the parameters you want to chane in the following file:')
    print(ini_file)
    print('After finished, please enter any Alphabeta to continue the programm.')
    #key = input()
    key = 1
    if key != None:
        parameters = read_change_parameters(ini_file)
        for job in jobs:
            job_path = job.path
            change_parameter(job_path, parameters)
            print(job)
            print('INPUT file has changed...')


def creat_ini_file(ini_path):
    ini_file = os.path.join(ini_path, 'change_parameters.ini')
    # with open(ini_file, 'w') as f:
    #     f.write(';jobs_not_converged.ini\n')
    #     f.write(';initial input file for change some parameters in CRYSTAL calculation\n')
    #     f.write('\n')
    #     f.write('\n')
    #     f.write('[parameters]\n')
    #     f.write(';Please use one line to write values for one paramete and strictly adhere to the CRYSTAL format.\n')
    #     f.write(';If needed, use \'\\n\' to represent Enter')
    #     f.write(';For Example:\n')
    #     f.write(';parameter1 = FMIXING\n')
    #     f.write(';value1 = 80\n')
    #     f.write(';parameter2 = SETINF\n')
    #     f.write(';value2 = 2\\n41 30\\n43 20\n')
    return ini_file


def read_change_parameters(ini_file):
    cfg = ConfigParser()
    cfg.read(ini_file, encoding='utf-8')
    options = cfg.options('parameters')
    names = [para for para in options if para.startswith('parameter')]
    names_dict = {get_nu(para): cfg.get('parameters', para) for para in names}
    values = [v for v in options if v.startswith('value')]
    values_dict = {get_nu(v): cfg.get('parameters', v) for v in values}
    parameters = {}
    for key in names_dict.keys():
        parameters[names_dict[key]] = values_dict[key]
    return parameters


def get_nu(name):
    name = name.split('_')
    nu = int(name[-1])
    return nu

def change_parameter(path, parameters):
    input_file = os.path.join(path, 'INPUT')
    with open(input_file, 'r') as f:
        lines = f.readlines()
    for key, value in parameters.items():
        lines_num, split_value = cal_line_num(value)
        if key+'\n' in lines:
            i = lines.index(key+'\n')
            j = 1
            while j <= lines_num:
                lines[i+j] = split_value[j-1] + '\n'
                j += 1
        else:
            i = lines.index('EXCHSIZE\n')
            lines.insert(i, key + '\n')
            j = 1
            while j <= lines_num:
                lines.insert(i+j, split_value[j-1] + '\n')
                j += 1
    with open(input_file, 'w') as f:
        f.writelines(lines)


def cal_line_num(value):
    lines = value.split('\\n')
    return len(lines), lines



