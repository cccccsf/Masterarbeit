#!/usr/bin/python3
import os
import json
import sys
from Common.file_processing import mkdir
from Common import Job
from Crystal import Geometry
from Crystal import choose_shrink
from Crystal import Basis_set


class Input(object):

    def __init__(self, job, name, slab_or_molecule, layer_group, bs_type, layertype='bilayer', fiexed_atoms=[], cal_parameters={}, geometry={}, lattice_parameters={}):
        self.job_GeoOpt = job
        self.layertype = layertype
        self.job_hf1 = self.get_new_job()
        self.job_path = self.job_hf1.path
        self.input_path = os.path.join(self.job_path, 'INPUT')

        self.name = name
        self.slab_or_molecule = slab_or_molecule
        self.layer_group = layer_group
        self.fixed_atoms = fiexed_atoms

        self.original_lattice_parameter = lattice_parameters
        self.lattice_parameter = self.get_lattice_parameter()
        self.original_geometry = geometry
        self.geometry = self.get_geometry()
        self.number_of_atoms = len(self.geometry)
        self.elements = []

        self.bs_type = bs_type
        self.bs = Basis_set(self.geometry.elements, 'HF1', self.bs_type)
        self.cal_parameters = cal_parameters

    def get_lattice_parameter(self):
        if self.original_lattice_parameter == {}:
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
        else:
            return self.original_lattice_parameter

    def get_geometry(self):
        if self.original_geometry == {}:
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
                sys.exit()	# here need a better way to deal with
            return geometry
        else:
            return self.original_geometry

    def get_new_job(self):
        path_GeoOpt = self.job_GeoOpt.path
        path_hf1 = path_GeoOpt.replace('geo_opt', 'hf1')
        if self.layertype != 'bilayer':
            path_hf1 = os.path.join(path_hf1, self.layertype)
        job_hf1 = Job(path_hf1)
        return job_hf1

    def write_basis_info(self):
        mkdir(self.job_path)
        with open(self.input_path, 'w') as f:
            f.write(self.name + '\n')
            f.write(self.slab_or_molecule + '\n')
            f.write(str(self.layer_group) + '\n')

    def write_lattice_parameter(self):
        if self.lattice_parameter != [[], []]:
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
        if len(self.cal_parameters) > 0:
            self.change_cal_parameters()

    def change_cal_parameters(self):
        with open(self.input_path, 'r') as f:
            lines = f.readlines()
        cal_begin = 0
        for i in range(len(lines)):
            if 'SHRINK' in lines[i]:
                cal_begin = i
        for key, value in self.cal_parameters.items():
            loc = self.if_para_in_input(key, lines)
            values_lines = value.split('\\n')
            # values_lines = values_lines.split('\\n')
            len_paras = len(values_lines)
            if loc > 0:
                for i in range(len_paras):
                    lines[loc+1+i] = values_lines[i]+'\n'
            else:
                lines.insert(cal_begin, key.upper()+'\n')
                for i in range(len_paras):
                    lines.insert(cal_begin+1+i, values_lines[i]+'\n')
        with open(self.input_path, 'w') as f:
            f.writelines(lines)

    @staticmethod
    def if_para_in_input(key, lines):
        loc = 0
        for i in range(len(lines)):
            if key.upper() in lines[i]:
                loc = i
                # print(loc)
        return loc




#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# aa = Gen_Inp(path)
# aa.gen_input()

# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv'
# hf1_bs_type=read_inp(path)
# print(hf1_bs_type)
