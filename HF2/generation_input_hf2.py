#!/usr/bin/python3
import os
import re
import sys
import json
from copy import deepcopy
from Crystal import Guesdual
from Crystal import Basis_set
from Crystal import Geometry
from Crystal import choose_shrink
from Common.file_processing import mkdir
from Common.job import Job
from HF1 import if_cal_finish



def get_jobs(path):
    path = os.path.join(path, 'hf1')
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if ('hf.out' in files) and ('fort.9' in files):
            new_path = root
            new_job = Job(new_path)
            if if_cal_finish(new_job):
                jobs.append(new_job)
    return jobs


class Input(object):

    def __init__(self, hf1_job, name, slab_or_molecule, layer_group, bs_type='default', layertype = 'bilayer', fixed_atoms = []):
        self.hf1_job = hf1_job     #class Job_path
        self.hf2_job = self.get_new_path()           #calss Job_path
        self.job_path = self.hf2_job.path
        self.input_path = os.path.join(self.job_path, 'INPUT')

        self.name = name
        self.slab_or_molecule = slab_or_molecule
        self.layer_group = layer_group
        self.fixed_atoms = fixed_atoms
        self.geometry = self.get_geometry()         #class geometry
        self.lattice_parameter = self.get_lattice_parameter()

        self.bs = []                #class Basis_set
        self.bs_type = 'default'


    def get_new_path(self):
        hf2_job = deepcopy(self.hf1_job)
        hf2_job.reset('method', 'hf2')
        return  hf2_job


    def get_geometry(self):
        path = self.hf1_job.root_path
        json_file = os.path.join(path, 'opt_geo_and_latt.json')
        with open(json_file, 'r') as f:
            data = json.load(f)
        geo_data = data['geometry']
        coor = '({}, {})'.format(self.hf1_job.x, self.hf1_job.z)
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
            sys.exit()	#here need a better way to deal with
        return geometry


    def get_lattice_parameter(self):
        path = self.hf1_job.root_path
        json_file = os.path.join(path, 'opt_geo_and_latt.json')
        with open(json_file, 'r') as f:
            data = json.load(f)
        data_latt = data['lattice_parameter']
        coor = '({}, {})'.format(self.hf1_job.x, self.hf1_job.z)
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
        if len(self.bs) == 0:
            self.generate_bs()
        self.bs.write_bs(self.input_path)
        with open(self.input_path, 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            f.write('END' + '\n')


    def generate_bs(self):
        self.bs = Basis_set(self.geometry.elements, 'HF2', self.bs_type)



    def guesdual(self):
        guesdual = Guesdual(self.bs)
        guesdual.write_guesdual(self.input_path)


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


    def write_end(self):
        with open(self.input_path, 'a') as f:
            f.write('END' + '\n')
            f.write('END' + '\n')


    def gen_input(self):
        self.write_basis_info()
        self.write_lattice_parameter()
        self.write_geometry()
        self.write_bs()
        self.write_cal_info()
        self.guesdual()
        self.write_end()




# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\hf_1\\x_-0.150\\z_-0.106'
# hf1_job = Job_path(path)
# Inp = Input(hf1_job)
# Inp.write_bs()
# print(Inp.new_path)
# Inp.gen_input()
# Inp.gen_input()
# Inp.write_metal_bs_default(15)
# get_bs_type(path)
