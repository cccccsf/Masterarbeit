#!/usr/bin/python3

import os
import re
from copy import deepcopy
import Initialization
from Common.file_processing import mkdir
from Common.test_variable import test_bs_type
from Common import read_pob_tzvp_bs
from Common import choose_bs
from geometry_optimization import read_input
from HF1 import default_basis_set


def get_job_dirs(path):
    path = path + '/hf1/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'hf.out' in files:
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
    hf2_block = lines[(sep[4]+1):(sep[5]+1)]
    blocks = []
    blocks.append(geo_block)
    blocks.append(bs_block)
    blocks.append(func_block)
    blocks.append(cal_block)
    blocks.append(hf1_block)
    blocks.append((hf2_block))
    return blocks


def read_inp(path):
    lines = read_input.read_input_file(path)
    blocks = split_block(lines)
    hf2_block = blocks[-1]
    #print(hf2_block)
    if len(hf2_block) == 1:
        hf2_bs_type = 'default'
    elif len(hf2_block) == 2:
        hf2_bs_type = hf2_block[0]
    if test_bs_type(hf2_bs_type):
        return hf2_bs_type
    else:
        print(hf2_bs_type)
        print('''
basis set type not correct!!!
Please correct and restart computation from HF1 setp!!!
''')
        read_input.exit_programm()
        return None


class Input(object):

    def __init__(self, path):
        self.path = path
        self.root_path = ''
        self.new_path = ''
        self.if_bs_change = 0
        self.geo_block = []
        self.job_name = '/hf_2'
        self.layertype = 'bilayer'
        self.z_dirname = ''
        self.x_dirname = ''
        self.distance = 0
        self.displacement = 0
        self.geometry = []
        self.bs_type = 'default'
        self.elements = []
        self.ele_to_bs_type = {}
        self.if_metals = []
        self.ele_nsh = {}
        self.ele_nu = {}
        self.nfr = 0

    def read_hf1_input(self):
        file = self.path + '/INPUT'
        with open(file) as f:
            lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split()) + '#'
        lines = re.split(':', lines.replace(': ', ':'))
        #print(lines)
        sep = []
        for num, line in enumerate(lines):
            if line == 'END':
                sep.append(num)
        # blocks = []
        geo_block = lines[:(sep[0]+1)]
        # bs_block= lines[(sep[0]+1):(sep[1]+1)]
        # cal_block = lines[(sep[1]+1):(sep[2]+1)]
        # blocks = []
        # blocks.append(geo_block)
        # blocks.append(bs_block)
        # blocks.append(cal_block)
        return geo_block


    def get_dist_and_disp(self):
        z = os.path.split(self.path)[-1]
        path = os.path.split(self.path)[0]
        self.layertype = 'bilayer'
        if z == 'underlayer' or z =='upperlayer':
            self.layertype = z
            z = os.path.split(path)[-1]
            path  = os.path.split(path)[0]
        self.z_dirname = z
        z = float(z.split('_')[-1])
        self.distance = z
        x = os.path.split(path)[-1]
        root_path = os.path.split(path)[0]
        self.x_dirname = x
        x = float(x.split('_')[-1])
        self.displacement = x
        self.root_path = os.path.split(root_path)[0]


    def get_geometry(self):
        with open(self.root_path + '/geo_opt/' + self.x_dirname + '/' + self.z_dirname + '/optimized_geometry', 'r') as f:
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


    def write_geo_block(self):
        if self.layertype == 'bilayer':
            self.new_path = self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname
        elif self.layertype == 'underlayer' or self.layertype == 'upperlayer':
            self.new_path = self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/' + self.layertype
        mkdir(self.new_path)
        with open(self.new_path + '/INPUT', 'w') as f:
            for line in self.geo_block:
                f.write(line + '\n')


    def add_shells(self, bs):
        """
        add 1/3 of the d and f orbitals from HF1
        :param bs: basis set
        :return: new basis set
        """
        add_d = []
        add_f = []
        for shell in bs:
            if str(shell[0][1]) == '3':
                add_d.append(deepcopy(shell))
            elif str(shell[0][1]) == '4':
                add_f.append(deepcopy(shell))
        for shell in add_d:
            for i in range(1,len(shell)):
                shell[i][0] = str(float(shell[i][0])/3)
        for shell in add_f:
            for i in range(1,len(shell)):
                shell[i][0] = str(float(shell[i][0])/3)
        #print(bs)
        new_bs = bs + add_d + add_f
        #print(new_bs)
        return new_bs


    def write_metal_bs_default(self, element):
        head, bs = read_pob_tzvp_bs.read_pob_bs(element)
        basis_set = read_pob_tzvp_bs.transfer_to_target_bs(bs)
        new_bs = self.add_shells(basis_set)
        new_head = head.split(' ')
        self.ele_nsh[element] = new_head[1]
        new_head[1] = str(len(new_bs))
        self.ele_nu[element] = int(new_head[1]) - int(self.ele_nsh[element])
        with open(self.new_path + '/INPUT', 'a') as f:
            for unit in new_head:
                f.write(str(unit) + ' ')
            f.write('\n')
            for shell in new_bs:
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
        #print(bs)
        self.ele_nsh[element] = len(bs)
        new_bs = self.add_shells(bs)
        self.ele_nu[element] = len(new_bs) - int(self.ele_nsh[element])
        #print(new_bs)
        with open(self.new_path + '/INPUT', 'a') as f:
            f.write(str(element) + ' ' + str(len(new_bs)) + '\n')
            for shell in new_bs:
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
        Bs_Init = Initialization.Bs_Init(self.geometry, self.bs_type)
        self.ele_to_bs_type, self.elements = Bs_Init.gen_bs_info(self.if_bs_change)
        basis_arrays = []
        for key,value in self.ele_to_bs_type.items():
            bs_array = choose_bs.read_basis_set_file(key, value)
            basis_arrays.append(bs_array)
        basis_arrays = choose_bs.transfer_crystal_formatted_bs_input(basis_arrays, self.ele_to_bs_type.keys())
        new_bs_arrays = []
        j = 0
        for element in basis_arrays:
            self.ele_nsh[self.elements[j]] = len(element)
            new_bs = self.add_shells(element)
            self.ele_nu[self.elements[j]] = len(new_bs) - int(self.ele_nsh[self.elements[j]])
            new_bs_arrays.append(new_bs)
            j += 1
        # print(self.ele_nu)
        # print(self.ele_nsh)
        i = 0
        with open(self.new_path + '/INPUT', 'a') as f:
            for element in new_bs_arrays:
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
        with open(self.new_path + '/INPUT', 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            f.write('END' + '\n')


    def guesdual(self):
        nfr = 0    #number of modification in the atomic basis set given in input
        ic = 0
        ele_with_mod = []
        for element in self.elements:
            if element in self.ele_nsh:
                nfr += 1
                ele_with_mod.append(element)
        with open(self.new_path+ '/INPUT', 'a') as f:
            f.write('GUESDUAL' + '\n')
            f.write(str(nfr) + ' ' + str(ic) +'\n')
            for ele in ele_with_mod:
                f.write(str(ele) + ' ' + str(self.ele_nsh[ele]) + ' ' + str(self.ele_nu[ele]))
                f.write('\n')
            f.write('END' + '\n')


    def write_cal_info(self):
        with open(self.new_path+ '/INPUT', 'a') as f:
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


    def write_end(self):
        with open(self.new_path+ '/INPUT', 'a') as f:
            f.write('END' + '\n')
            f.write('END' + '\n')



    def gen_input(self):
        self.geo_block = self.read_hf1_input()
        self.get_dist_and_disp()
        self.geometry = self.get_geometry()
        self.bs_type = read_inp(self.root_path)
        if self.bs_type == 'default':
            self.if_bs_change = 0
        else:
            self.if_bs_change = 1
        self.write_geo_block()
        self.write_bs()
        self.write_cal_info()
        self.guesdual()
        self.write_end()





#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\hf_1\\x_-0.150\\z_-0.106'
# Inp = Input(path)
# Inp.gen_input()
#Inp.write_metal_bs_default(15)
#get_bs_type(path)
