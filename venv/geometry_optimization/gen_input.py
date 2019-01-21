#!/usr/bin/python3
import os
import time
import json
from Data import Functionals
from Data import Grimme_parameter
from Common.file_processing import mkdir
from Crystal import Basis_set
from Crystal import choose_shrink
import Initialization


class Geo_Opt_Input(object):

    def __init__(self, job, name, slab_or_molecule, layer_group, lattice_vector, geometry, bs_type, functional = 'PBE0'):
        self.job = job
        self.dir_path = job.path
        self.input_path = os.path.join(self.dir_path, 'INPUT')

        self.name = name
        self.slab_or_molecule = slab_or_molecule
        self.layer_group = layer_group
        self.lattice_vector = lattice_vector
        self.geometry = geometry
        self.elements = self.geometry.elements
        self.number_of_atoms = len(self.geometry)

        self.bs = []    #class Basis Set
        self.bs_type = bs_type

        self.functional = functional



    def write_basic_info(self):
        mkdir(self.dir_path)
        with open(self.input_path, 'w') as f:
            f.write(self.name + '\n')
            f.write(self.slab_or_molecule + '\n')
            f.write(str(self.layer_group) + '\n')


    def write_lattice_parameter(self):
        with open(self.input_path, 'a') as f:
            for l in self.lattice_vector[0]:
                f.write(str(l) + ' ')
            for a in self.lattice_vector[1]:
                f.write(str(a) + ' ')
            f.write('\n')


    def write_opt_info(self):
        free_atoms = self.geometry.z_free_no
        number_of_free_atoms = len(free_atoms)
        with open(self.input_path, 'a') as f:
            f.write('OPTGEOM' + '\n')
            f.write('FRAGMENT' + '\n')
            f.write(str(number_of_free_atoms) + '\n')
            for atom in free_atoms:
                f.write(str(atom) + ' ')
            f.write('\n')
            f.write('ENDOPT' + '\n')
            f.write('END' + '\n')


    def write_bs(self):
        self.bs = Basis_set(self.geometry.elements, 'GEO_OPT', self.bs_type)
        self.bs.write_bs(self.input_path)
        with open(self.input_path, 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            f.write('END' + '\n')


    def write_functional(self):
        with open(self.input_path, 'a') as f:
            f.write('DFT' + '\n')
            if self.functional in Functionals.functionals:
                self.functional = Functionals.functionals[self.functional]
            f.write(self.functional + '\n')
            f.write('XLGRID' + '\n')
            f.write('END' + '\n')

    def write_grimme_dispersion(self):
        with open(self.input_path, 'a') as f:
            f.write('GRIMME' + '\n')
            f.write('1.05' + ' ' + '20.' +  ' ' + '25.' + '\n')
            elements = self.bs.elements_unique
            elements.sort()
            f.write(str(len(elements)) + '\n')
            for element in elements:
                f.write(str(element) + ' ')
                element = int(element)
                f.write(str(Grimme_parameter.C6[element]) + ' ')
                f.write(str(Grimme_parameter.R0[element]))
                f.write('\n')

    def write_other_info(self):
        shrink = choose_shrink(self.lattice_vector)
        shrink = str(shrink)
        with open(self.input_path, 'a') as f:
            f.write('SHRINK' + '\n')
            f.write(shrink + ' ' + shrink + '\n')
            f.write('TOLINTEG' + '\n')
            f.write('10' + ' ' + '10' + ' ' + '10' + ' ' + '25' + ' ' + '75' + '\n')
            f.write('MAXCYCLE' + '\n')
            f.write('60' + '\n')
            f.write('FMIXING' + '\n')
            f.write('80' + '\n')
            f.write('ANDERSON' + '\n')
            f.write('EXCHSIZE' + '\n')
            f.write('30000000' + '\n')
            f.write('BIPOSIZE' + '\n')
            f.write('30000000' + '\n')
            f.write('END' + '\n')
            f.write('END' + '\n')
            f.write('END' + '\n')

    def write_gussp(self):
        with open(self.input_path, 'a') as f:
            f.write('GUESSP' + '\n')


    def write_cal_input(self):
        self.write_functional()
        self.write_grimme_dispersion()
        if self.job.z != '0' or self.job.x != '0':
            self.write_gussp()
        self.write_other_info()
        print('INPUT file generated...')


    def gen_input(self):
        self.write_basic_info()
        self.write_lattice_parameter()
        self.geometry.write_geometry(self.input_path)
        self.write_opt_info()
        self.write_bs()
        self.write_cal_input()



def get_and_write_init_distance(geometry, path):
    distance = geometry.layer_distance
    path = os.path.join(path, 'geo_opt')
    dis_path = os.path.join(path, 'init_distance')
    with open(dis_path, 'w') as f:
        f.write(str(distance) + '\n')


def creat_geo_lat_json(path):
    geo_lat_json = {'geometry': {}, 'lattice_parameter': {}}
    json_path = os.path.join(path, 'opt_geo_and_latt.json')
    print(json_path)
    with open(json_path, 'w') as f:
        json.dump(geo_lat_json, f, indent=4)
