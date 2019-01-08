#!/usr/bin/python3

import os
import re
from copy import deepcopy
import Initialization
import Crystal
from read_input import Read_input
from Common.file_processing import mkdir
from Common.test_variable import test_bs_type
from Common import read_pob_tzvp_bs
from Common import choose_bs
from Common.job_path import Job_path
from geometry_optimization import read_input
from HF1 import default_basis_set


def get_job_dirs(path):
    path = path + '/hf_1/'
    walks = os.walk(path)
    job_dirs = []
    for root, dirs, files in walks:
        if 'hf.out' in files:
            job_dirs.append(root)
    return job_dirs


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

    def __init__(self, hf1_job):
        self.hf1_path = hf1_job     #class Job_path
        self.hf2_path = 0           #calss Job_path
        self.get_new_path()

        self.geometry = []          #class geometry
        self.init_geometry()

        self.Read_input = 0
        self.bs = []                #class Basis_set
        self.bs_type = 'default'
        self.read_original_input()

        self.new_path = self.hf2_path.path
        self.if_bs_change = 0
        self.geo_block = []


    def read_hf1_input(self):
        file = self.hf1_path.path + '/INPUT'
        with open(file) as f:
            lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split()) + '#'
        lines = re.split(':', lines.replace(': ', ':'))
        #print(lines)
        sep = []
        for num, line in enumerate(lines):
            if line == 'END':
                sep.append(num)
        geo_block = lines[:(sep[0]+1)]

        return geo_block

    def init_geometry(self):
        if self.hf1_path.layertype == 'bilayer':
            path = self.hf1_path.path.replace('hf_1', 'geo_opt')
        else:
            path = self.hf1_path.path.replace('hf_1', 'geo_opt')
            path = os.path.split(path)[0]
        self.geometry = Crystal.Geometry(path)

    def get_new_path(self):
        hf2_path = deepcopy(self.hf1_path)
        hf2_path.reset('method', 'hf_2')
        self.hf2_path = hf2_path


    def write_geo_block(self):
        mkdir(self.new_path)
        with open(self.new_path + '/INPUT', 'w') as f:
            for line in self.geo_block:
                f.write(line + '\n')


    def write_bs(self):
        self.bs = Crystal.Basis_set(self.geometry.elements, 'HF2', self.bs_type)
        self.bs.write_bs(self.new_path + '/INPUT')
        with open(self.new_path + '/INPUT', 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            f.write('END' + '\n')


    def guesdual(self):
        guesdual = Crystal.Guesdual(self.bs)
        guesdual.write_guesdual(self.new_path + '/INPUT')


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

    def read_original_input(self):
        self.Read_input = Read_input(self.hf1_path.root_path)
        self.bs_type = self.Read_input.hf2_bs

    def gen_input(self):
        self.geo_block = self.read_hf1_input()
        self.write_geo_block()
        self.write_bs()
        self.write_cal_info()
        self.guesdual()
        self.write_end()




# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\hf_1\\x_-0.150\\z_-0.106'
# hf1_path = Job_path(path)
# Inp = Input(hf1_path)
# Inp.write_bs()
# print(Inp.new_path)
# Inp.gen_input()
# Inp.gen_input()
# Inp.write_metal_bs_default(15)
# get_bs_type(path)
