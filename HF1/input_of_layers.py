#!/usr/bin/python3
import os
from Common import Job_path
from HF1 import Input
from copy import deepcopy

class Layer_Inp(Input):

    def __init__(self, job, name, slab_or_molecule, layer_group, bs_type, layertype, fiexed_atoms = []):
        super(Layer_Inp, self).__init__(job, name, slab_or_molecule, layer_group, bs_type, layertype=layertype, fiexed_atoms=fiexed_atoms)
        self.ghost_info = self.get_ghost()


    def get_ghost(self):
        count = 1
        geo_z = [float(i) for i in self.geometry.z]
        fixed_z = [float(i) for i in self.geometry.z_fixed_co]
        th = (self.geometry.layer_distance)/7
        under, upper = [], []
        for z in geo_z:
            if z <= min(fixed_z) or abs(z - min(fixed_z)) <= th:
                under.append(count)
            else:
                upper.append(count)
            count += 1
        if self.layertype == 'underlayer':
            return upper
        else:
            return under


    def write_ghost(self):
        with open(self.input_path, 'a') as f:
            f.write('GHOSTS' + '\n')
            f.write(str(len(self.ghost_info)) + '\n')
            for atom in self.ghost_info:
                f.write(str(atom) + ' ')
            f.write('\n')


    def write_bs(self):
        self.bs.write_bs(self.input_path)
        with open(self.input_path, 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
        self.write_ghost()
        with open(self.input_path, 'a') as f:
            f.write('END' + '\n')



class Under_Layer_Inp(Input):

    def __init__(self, path, if_bs_change = 0, ele_to_bs_type=[], elements=[], root_path=''):
        super(Under_Layer_Inp, self).__init__(path, if_bs_change = 0, ele_to_bs_type=[], elements=[], root_path='')
        self.underlayer = []
        self.n_fixed_atoms = []
        self.z_fixed_atoms = []
        self.ghost_number = []


    def transfer_to_float(self):
        self.get_geometry()
        new_geo = []
        for atom in self.geometry:
            if type(atom) == str:
                atom = atom.split()
            new_atom = []
            for unit in atom:
                new_unit = float(unit)
                new_atom.append(new_unit)
            new_geo.append(new_atom)
        return new_geo


    def gen_fixed_atoms(self):
        count = 1
        geo_info_with_number = deepcopy(self.geometry)
        for atom in geo_info_with_number:
            atom.insert(0, count)
            count += 1
        z_coordinates = []
        z_coordinates_with_num = {}
        z_coordinates_with_num_re = {}
        for atom in geo_info_with_number:
            z_coordinates_with_num[atom[0]] = atom[4]
            z_coordinates_with_num_re[atom[4]] = atom[0]
            z_coordinates.append(atom[4])
        z_coordinates.sort()
        i = 1
        while i < len(z_coordinates):
            if abs(z_coordinates[i] - z_coordinates[i-1]) < 0.1:
                z_coordinates.pop(i)
            else:
                i += 1
        distance = 0
        z_fixed_atoms = [0, 0]
        for i in range(1, len(z_coordinates)):
            if (abs(z_coordinates[i] - z_coordinates[i-1])) > distance:
                distance = abs(z_coordinates[i] - z_coordinates[i-1])
                z_fixed_atoms[1] = (z_coordinates[i])
                z_fixed_atoms[0] = (z_coordinates[i-1])
        self.z_fixed_atoms = z_fixed_atoms
        self.n_fixed_atoms.append(z_coordinates_with_num_re[z_fixed_atoms[0]])
        self.n_fixed_atoms.append(z_coordinates_with_num_re[z_fixed_atoms[1]])
        #return n_fixed_atoms


    def get_underlayer(self):
        count = 1
        for atom in self.geometry:
            if atom[3] <= min(self.z_fixed_atoms) or abs(atom[3] - min(self.z_fixed_atoms)) <= 0.1:
                self.underlayer.append(atom)
            else:
                self.ghost_number.append(count)
            count += 1


    def write_layer(self):
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            for line in self.underlayer:
                for unit in line:
                    f.write(str(unit) + ' ')
                f.write('\n')
            f.write('END' + '\n')


    def write_geo(self):
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            for line in self.geometry:
                for unit in line:
                    f.write(str(unit) + ' ')
                f.write('\n')
            f.write('END' + '\n')


    def write_ghost(self):
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write('GHOSTS' + '\n')
            f.write(str(len(self.ghost_number)) + '\n')
            for atom in self.ghost_number:
                f.write(str(atom) + ' ')
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
        self.write_ghost()
        with open(self.root_path + self.job_name + '/' + self.x_dirname + '/' + self.z_dirname + '/INPUT', 'a') as f:
            f.write('END' + '\n')


    def write_underlayer_inp_init(self):
        self.geometry = self.transfer_to_float()
        self.gen_fixed_atoms()
        self.get_underlayer()
        self.get_basis_info()
        self.get_dist_and_disp()
        self.get_lattice_parameter()
        self.z_dirname = self.z_dirname + '/underlayer'
        self.write_basis_info()
        self.write_lattice_para()
        self.write_geo()
        self.write_bs()
        self.write_cal_info()


    def write_underlayer_inp(self):
        self.geometry = self.transfer_to_float()
        self.gen_fixed_atoms()
        self.get_underlayer()
        self.get_basis_info()
        self.get_dist_and_disp()
        self.get_lattice_parameter()
        self.z_dirname = self.z_dirname + '/underlayer'
        self.write_basis_info()
        self.write_lattice_para()
        self.write_geo()
        self.write_bs()
        self.write_gussp()
        self.write_cal_info()




# p = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv/geo_opt/x_-0.150\\z_-0.106'
# Under = Upper_Layer_Inp(p)
# Under.write_upperlayer_inp()
# Upper = Upper_Layer_Inp(p)
# Upper.write_upperlayer_inp()

