#!/usr/bin/python3

import os
import re
from Common.file_processing import mkdir
from Common.test_variable import test_bs_type
from Common import read_pob_tzvp_bs
from Common import choose_bs
from geometry_optimization import read_input
from HF1 import default_basis_set


def get_job_dirs(path):
    path = path + '/geo_opt/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'geo_opt.out' in files:
            job_dirs.append(root)
    return job_dirs


def split_block(lines):
    sep = []
    for num, line in enumerate(lines):
        if line == 'END':
            sep.append(num)
    geo_block = lines[:(sep[0]+1)]
    bs_block= lines[(sep[0]+1):(sep[1]+1)]
    func_block = lines[(sep[1]+1):(sep[2]+1)]
    cal_block = lines[(sep[2]+1):(sep[3]+1)]
    hf1_block = lines[(sep[3]+1):(sep[4]+1)]
    blocks = []
    blocks.append(geo_block)
    blocks.append(bs_block)
    blocks.append(func_block)
    blocks.append(cal_block)
    blocks.append(hf1_block)
    return blocks


def read_inp(path):
    lines = read_input.read_input_file(path)
    blocks = split_block(lines)
    hf_block = blocks[-1]
    if len(hf_block) == 1:
        hf1_bs_type = 'default'
    elif len(hf_block) == 2:
        hf1_bs_type = hf_block[0]
    if test_bs_type(hf1_bs_type):
        return hf1_bs_type
    else:
        print(hf1_bs_type)
        print('''
basis set type not correct!!!
Please correct and restart computation from HF1 setp!!!
''')
        read_input.exit_programm()


class Gen_Inp(object):

    def __init__(self, path, if_bs_change = 0, ele_to_bs_type=[], elements=[], root_path=''):
        self.path = path
        self.root_path = root_path
        self.basis_info = []
        self.number_of_atoms = 0
        self.lattice_parameter = []
        self.geometry = []
        self.job_name = '/hf_1'
        self.z_dirname = ''
        self.x_dirname = ''
        self.if_bs_change = if_bs_change
        self.distance = 0
        self.displacement = 0
        self.elements = elements
        self.ele_to_bs_type = ele_to_bs_type
        self.if_metals = []


    def get_basis_info(self):
        f = open(self.path + '/INPUT', 'r')
        lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split()) + '#'
        f.close()
        lines = re.split(':', lines.replace(': ', ':'))
        self.basis_info = lines[:3]
        self.number_of_atoms = lines[4]


    def get_lattice_parameter(self):
        with open(self.path + '/optimized_lattice_parameter', 'r') as f:
            line = f.read()
        self.lattice_parameter = line.split()


    def get_geometry(self):
        with open(self.path + '/optimized_geometry', 'r') as f:
            lines = f.read()
        lines = lines.split('\n')
        i = 0
        for line in lines:
            if line == '':
                del lines[i]
            else:
                i += 1
        self.geometry = lines
        return lines


    def get_dist_and_disp(self):
        z = os.path.split(self.path)[-1]
        x = os.path.split(self.path)[0]
        root_path = os.path.split(x)[0]
        x = os.path.split(x)[-1]
        self.z_dirname = z
        self.x_dirname = x
        self.distance = z.split('_')[-1]
        self.displacement = x.split('_')[-1]
        self.root_path = os.path.split(root_path)[0]


    def write_basis_info(self):
        mkdir(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname)
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'w') as f:
            for line in self.basis_info:
                f.write(line + '\n')


    def write_lattice_para(self):
        if self.basis_info[1].strip().upper() == 'SLAB':
            lattice_parameter = self.lattice_parameter[0:2]
            lattice_parameter.append(self.lattice_parameter[-1])
            with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
                for unit in lattice_parameter:
                    f.write(unit + ' ')
                f.write('\n')
                f.write(self.number_of_atoms + '\n')
        else:
            with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
                for unit in self.lattice_parameter:
                    f.write(unit + ' ')
                    f.write(self.number_of_atoms + '\n')


    def write_geometry(self):
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            for line in self.geometry:
                f.write(line + '\n')
            f.write('END' + '\n')


    def write_metal_bs_default(self, element):
        head, bs = read_pob_tzvp_bs.read_pob_bs(element)
        basis_set = read_pob_tzvp_bs.transfer_to_target_bs(bs)
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write(head+ '\n')
            for shell in basis_set:
                for line in shell:
                    for unit in line:
                        f.write(str(unit) + ' ')
                    f.write('\n')


    def write_non_metal_bs_default(self, element):
        bs_ahlrichs = choose_bs.read_basis_set_file(element, 'Ahlrichs_VTZ')
        bs_cc = choose_bs.read_basis_set_file(element, 'cc-PVTZ')
        bs_combine = []
        for shell_ahl in bs_ahlrichs:
            #print(shell_ahl)
            if shell_ahl[0][0] == 'S' or shell_ahl[0][0] == 'SP' or shell_ahl[0][0] == 'P':
                bs_combine.append(shell_ahl)
        for shell_cc in bs_cc:
            if shell_cc[0][0] == 'D' or shell_cc[0][0] == 'F':
                bs_combine.append(shell_cc)
        elements = []
        elements.append(element)
        bs_arrays = []
        bs_arrays.append(bs_combine)
        bs = choose_bs.transfer_crystal_formatted_bs_input(bs_arrays, elements)
        bs = bs[0]
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write(str(element) + ' ' + str(len(bs)) + '\n')
            for shell in bs:
                for line in shell:
                    for unit in line:
                        f.write(str(unit) + ' ')
                    f.write('\n')


    def write_bs_default(self):
        for element, if_metal in dict(zip(self.elements, self.if_metals)).items():
            # print(element)
            # print(if_metal)
            if if_metal == 1:
                self.write_metal_bs_default(element)
            elif if_metal == 0:
                #print(element)
                self.write_non_metal_bs_default(element)


    def write_bs_with_type(self):
        basis_arrays = []
        for key,value in self.ele_to_bs_type.items():
            bs_array = choose_bs.read_basis_set_file(key, value)
            basis_arrays.append(bs_array)
        basis_arrays = choose_bs.transfer_crystal_formatted_bs_input(basis_arrays, self.ele_to_bs_type.keys())
        i = 0
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            for element in basis_arrays:
                f.write(str(self.elements[i]) + ' ' + str(len(element)) + '\n')
                for shell in element:
                    for line in shell:
                        for unit in line:
                            f.write(str(unit) + ' ')
                        f.write('\n')


    def write_bs(self):
        if self.if_bs_change == 0:
            self.ele_to_bs_type, self.elements, self.if_metals= default_basis_set.gen_bs_info(self.geometry)
            #print(self.geometry)
            self.write_bs_default()
        elif self.if_bs_change == 1:
            self.write_bs_with_type()
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            f.write('END' + '\n')


    def write_gussp(self):
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write('GUESSP' + '\n')


    def write_cal_info(self):
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write('SHRINK' + '\n')
            f.write('12' + ' ' + '12' + '\n')
            f.write('TOLINTEG' + '\n')
            f.write('15' + ' ' + '15' + ' ' + '15' + ' ' + '25' + ' ' + '75' + '\n')
            f.write('SETINF' + '\n')
            f.write('2' + '\n')
            f.write('41' + ' ' + '40' + '\n')
            f.write('43' + ' ' + '30' + '\n')
            f.write('MAXCYCLE' + '\n')
            f.write('60' + '\n')
            f.write('FMIXING' + '\n')
            f.write('60' + '\n')
            f.write('ANDERSON' + '\n')
            f.write('EXCHSIZE' + '\n')
            f.write('30000000' + '\n')
            f.write('BIPOSIZE' + '\n')
            f.write('30000000' + '\n')
            f.write('END' + '\n')
            f.write('END' + '\n')
            f.write('END' + '\n')


    def gen_input(self):
        self.get_basis_info()
        self.geometry = self.get_geometry()
        self.get_dist_and_disp()
        self.get_lattice_parameter()
        self.write_basis_info()
        self.write_lattice_para()
        self.write_geometry()
        self.write_bs()
        self.write_gussp()
        self.write_cal_info()


    def gen_input_init(self):
        self.get_basis_info()
        self.get_geometry()
        self.get_dist_and_disp()
        self.get_lattice_parameter()
        self.write_basis_info()
        self.write_lattice_para()
        self.write_geometry()
        self.write_bs()
        self.write_cal_info()




#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# aa = Gen_Inp(path)
# aa.gen_input()

# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv'
# hf1_bs_type=read_inp(path)
# print(hf1_bs_type)
