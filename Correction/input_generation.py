#!/usr/bin/python3
import os
import shutil

def copy_input(job):
    ziel_path = job.path
    original_input_file = job.parameter['original_input_file']
    file_name = os.path.split(original_input_file)[-1]
    inp_to = os.path.join(ziel_path, file_name)
    job.parameter['input_file'] = inp_to
    try:
        shutil.copy(original_input_file, inp_to)
    except Exception as e:
        print(e)


def add_geometry_name(job, xyz_name=''):
    input_file = job.parameter['input_file']
    with open(input_file, 'r') as f:
        lines = f.readlines()
    ind = 0
    for i in range(len(lines)):
        if lines[i].startswith('geometry'):
            ind = i
    if xyz_name == '':
        xyz_file = get_xyz_file(job.path)
    else:
        xyz_file = xyz_name
    geo_line = 'geometry={}\n'.format(xyz_file)
    if ind != 0:
        lines[ind] = geo_line
    else:
        lines.insert(8, geo_line)
    with open(input_file, 'w') as f:
        f.writelines(lines)
    return xyz_file


def get_xyz_file(path):
    xyz_files = [file for file in os.listdir(path) if file.endswith('.xyz')]
    if len(xyz_files) == 1:
        xyz = xyz_files[0]
    else:
        print('There are more than one .xyz geometry file in the following directory:')
        print(path)
        for f in xyz_files:
            print(f)
        print('Which one do you want to choose?')
        print('Please enter the exact name of the .xyz file or you can enter 0 to use the one with latest modified time.')
        while True:
            xyz = input()
            if xyz in xyz_files:
                break
            elif str(xyz) == '0':
                xyz = get_min_mtime(path, xyz_files)
                #print('xyz:', xyz)
                break
            else:
                print('Please enter the right name of geometry file name or 0')
    return xyz


def get_min_mtime(path, xyz_files):
    max_time = 0
    for file in xyz_files:
        file_path = os.path.join(path, file)
        mtime = os.path.getmtime(file_path)
        if mtime > max_time:
            xyz = file
    return xyz


def change_memory(job):
    input_file = job.parameter['input_file']
    with open(input_file, 'r') as f:
        lines = f.readlines()
    line_mem = 'memory,{},m\n'.format(job.parameter['memory'])
    ind = 10000
    for i in range(len(lines)):
        if lines[i].startswith('memory'):
            ind = i
    if ind != 10000:
        lines[ind] = line_mem
    else:
        lines.insert(1, line_mem)
    with open(input_file, 'w') as f:
        f.writelines(lines)

def generation_input(job, xyz_name=''):
    copy_input(job)
    if xyz_name == '':
        xyz_name = add_geometry_name(job)
    else:
        add_geometry_name(job, xyz_name)
    try:
        if job.parameter['memory'] != '':
            int(job.parameter['memory'])
            change_memory(job)
    except ValueError as e:
        print('No memory info changes.')
        print('Input file keeps the original value.')
    return xyz_name



