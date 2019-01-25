#!/usr/bin/python3

import os
import re
import json
from Common.file_processing import mkdir
from Common.test_variable import test_bs_type
from Common import read_pob_tzvp_bs
from Common import choose_bs
from Common import Job_path
from Crystal import Geometry
from Crystal import choose_shrink
from Crystal import Basis_set
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


class Input(object):

    def __init__(self, job, name, slab_or_molecule, layer_group, bs_type, fiexed_atoms):
        self.job_GeoOpt = job
        self.job_hf1 = self.get_new_job()
        self.job_path = self.job_hf1.path
        self.input_path = os.path.join(self.job_path, 'INPUT')

        self.name = name
        self.slab_or_molecule = slab_or_molecule
        self.layer_group = layer_group
        self.fixed_atoms = fiexed_atoms

        self.lattice_parameter = self.get_lattice_parameter()
        self.geometry = self.get_geometry()
        self.number_of_atoms = len(self.geometry)
        self.elements = []

        self.bs_type = bs_type
        self.bs = Basis_set(self.geometry.elements, 'HF1', self.bs_type)


    def get_lattice_parameter(self):
        path = self.job_GeoOpt.root_path
        json_file = os.path.join(path, 'opt_geo_and_latt.json')
        with open(json_file, 'r') as f:
            data = json.load(f)
        data_latt = data['lattice_parameter']
        coor = '({}, {})'.format(self.job_GeoOpt.x, self.job_GeoOpt.z)
        try:
            latt_para = data_latt[coor]
            latt_para = [float(i) for i in latt_para]
            if self.slab_or_molecule == 'SLAB' and len(latt_para) == 6:
                latt_para = latt_para[:2] + latt_para[-1:]
                l = latt_para[:2]
                a = latt_para[-1:]
                new_latt_patt = [l, a]
            elif len(latt_para) == 6:
                l = latt_para[:3]
                a = latt_para[3:]
                new_latt_patt = [l, a]
            else:
                l = [i for i in latt_para if i <= 20]
                a = [i for i in latt_para if i > 20]
                new_latt_patt = [l, a]
            return new_latt_patt
        except KeyError as e:
            print(e)
            print('Optimized lattice parameter not found!'
                  'Please check out?')
            return []


    def get_geometry(self):
        path = self.job_GeoOpt.root_path
        json_file = os.path.join(path, 'opt_geo_and_latt.json')
        with open(json_file, 'r') as f:
            data = json.load(f)
        geo_data = data['geometry']
        coor = '({}, {})'.format(self.job_GeoOpt.x, self.job_GeoOpt.z)
        try:
            geometry = geo_data[coor]
            if type(self.fixed_atoms) == list and len(self.fixed_atoms) == 2:
                geometry = Geometry(json_form=geometry, fixed_atoms=self.fixed_atoms)
            else:
                geometry = Geometry(json_form=geometry)
        except KeyError as e:
            print(e)
            print('Optimized lattice parameter not found!'
                  'Please check out?')
            geometry = []
        return geometry


    def get_new_job(self):
        path_GeoOpt = self.job_GeoOpt.path
        path_hf1 = path_GeoOpt.replace('geo_opt', 'hf_1')
        job_hf1 = Job_path(path_hf1)
        return job_hf1


    def write_basis_info(self):
        mkdir(self.job_path)
        with open(self.input_path, 'w') as f:
            f.write(self.name + '\n')
            f.write(self.slab_or_molecule + '\n')
            f.write(str(self.layer_group) + '\n')


    def write_lattice_parameter(self):
        with open(self.input_path, 'a') as f:
            for l in self.lattice_parameter[0]:
                f.write(str(l) + ' ')
            for a in self.lattice_parameter[1]:
                f.write(str(a) + ' ')
            f.write('\n')


    def write_geometry(self):
        self.geometry.write_geometry(self.input_path)
        with open(self.input_path, 'a') as f:
            f.write('END' + '\n')


    def write_bs(self):
        self.bs.write_bs(self.input_path)
        with open(self.input_path, 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            f.write('END' + '\n')


    def write_gussp(self):
        with open(self.input_path, 'a') as f:
            f.write('GUESSP' + '\n')


    def write_cal_info(self):
        shrink = choose_shrink(self.lattice_parameter)
        shrink = str(shrink)
        with open(self.input_path, 'a') as f:
            f.write('SHRINK' + '\n')
            f.write(shrink + ' ' + shrink + '\n')
            f.write('TOLINTEG' + '\n')
            f.write('10' + ' ' + '10' + ' ' + '10' + ' ' + '25' + ' ' + '75' + '\n')
            f.write('SETINF' + '\n')
            f.write('2' + '\n')
            f.write('41' + ' ' + '30' + '\n')
            f.write('43' + ' ' + '20' + '\n')
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
        self.write_basis_info()
        self.write_lattice_parameter()
        self.write_geometry()
        self.write_bs()
        if self.job_hf1.z != '0' or self.job_hf1.x != '0':
            self.write_gussp()
        self.write_cal_info()




#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# aa = Gen_Inp(path)
# aa.gen_input()

# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv'
# hf1_bs_type=read_inp(path)
# print(hf1_bs_type)
