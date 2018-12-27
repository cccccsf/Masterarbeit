#!/usr/bin/python3
import os
import time
from Common.choose_bs import read_basis_set_file
from Common.choose_bs import transfer_crystal_formatted_bs_input
from Data import Functionals
from Data import Grimme_parameter
from Common.file_processing import mkdir
import Initialization

class Geometry_Input(object):

    def __init__(self, path, name, slab_or_molecule, layer_group, lattice_vector, number_of_atoms, geometry_info, dirname):
        self.path = path
        self.name = name
        self.slab_or_molecule = slab_or_molecule
        self.layer_group = layer_group
        self.lattice_vector = lattice_vector
        self.number_of_atoms = number_of_atoms
        self.geometry_info = geometry_info
        self.dirname = '/geo_opt/' + str(dirname)

    def creat_input_file(self):
        mkdir(self.path + self.dirname)
        file = open(self.path + self.dirname + '/INPUT', 'w')
        file.close()
        #os.mknod(self.path + self.dirname + '/INPUT')

    def write_basic_info(self):
        with open(self.path + self.dirname + '/INPUT', 'w') as f:
            f.write(self.name + '\n')
            f.write(self.slab_or_molecule + '\n')
            f.write(str(self.layer_group) + '\n')
            #f.write(str(self.number_of_atoms) + '\n')

    def write_lattice_parameter(self):
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            for a in self.lattice_vector:
                f.write(str(a) + ' ')
            f.write('\n')

    def write_geo_info(self):
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write(str(self.number_of_atoms) + '\n')
            for atom in self.geometry_info:
                for coordinate in atom:
                    f.write(str(coordinate) + ' ')
                f.write('\n')

    def gen_input(self):
        self.creat_input_file()
        self.write_basic_info()
        self.write_lattice_parameter()
        self.write_geo_info()


class Opt_Input(object):

    def __init__(self, path, number_of_atoms, geometry_info, dirname, fixed_atoms = [0, 0]):
        self.number_of_atoms = number_of_atoms
        self.geometry_info = geometry_info
        self.fixed_atoms = fixed_atoms
        self.path = path
        self.dirname = '/geo_opt/' + str(dirname)

    def gen_fixed_atoms(self):
        #transfer coordinate from string to float
        geo_float = []
        for atom in self.geometry_info:
            new_atom = []
            for unit in atom:
                new_atom.append(float(unit))
            geo_float.append(new_atom)
        count = 1
        geo_info_with_number = geo_float
        for atom in geo_info_with_number:
            atom.insert(0, count)
            count += 1
        z_coordinates = []
        z_coordinates_with_num = {}
        z_coordinates_with_num_re = {}
        for atom in geo_info_with_number:
            z_coordinates_with_num[atom[0]] = atom[4]
            z_coordinates_with_num_re[atom[4]] = atom[0]    #re==reverse
            z_coordinates.append(atom[4])
        z_coordinates.sort()
        i = 1
        #dlete the repeat atom with the similar z-coordinate
        while i < len(z_coordinates):
        #for i in range(1, len(z_coordinates)):
            if abs(z_coordinates[i] - z_coordinates[i-1]) < 0.2:
                z_coordinates.pop(i)
            else:
                i += 1
        #print(z_coordinates)
        #get the longest distance between atom layer
        distance = 0
        z_fixed_atoms = [0, 0]
        #while i > 0 and i < len(z_coordinates):
        for i in range(1, len(z_coordinates)):
            if (abs(z_coordinates[i] - z_coordinates[i-1])) > distance:
                distance = abs(z_coordinates[i] - z_coordinates[i-1])
                z_fixed_atoms[0] = (z_coordinates[i])
                z_fixed_atoms[1] = (z_coordinates[i-1])
        #print(z_fixed_atoms)
        #get the serial number of the two fixed atoms
        n_fixed_atoms = []
        n_fixed_atoms.append(z_coordinates_with_num_re[z_fixed_atoms[0]])
        n_fixed_atoms.append(z_coordinates_with_num_re[z_fixed_atoms[1]])
        #print(n_fixed_atoms)
        return n_fixed_atoms

    def gen_free_atoms(self):
        free_atoms = []
        if  self.fixed_atoms == [0, 0]:
            self.fixed_atoms = self.gen_fixed_atoms()
        number_of_atoms = int(self.number_of_atoms)
        for i in range(1, number_of_atoms+1):
            if i != self.fixed_atoms[0] and i != self.fixed_atoms[1]:
                free_atoms.append(i)
        #print(self.fixed_atoms)
        #print(free_atoms)
        return free_atoms

    def write_opt_info(self):
        free_atoms = self.gen_free_atoms()
        number_of_free_atoms = int(self.number_of_atoms) - 2
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('OPTGEOM' + '\n')
            f.write('FRAGMENT' + '\n')
            f.write(str(number_of_free_atoms) + '\n')
            for atom in free_atoms:
                f.write(str(atom) + ' ')
            f.write('\n')
            f.write('ENDOPT' + '\n')
            f.write('END' + '\n')


class Basis_Set_Input(object):

    def __init__(self, path, ele_to_bs_type, dirname, if_bs_change = 0):
        self.ele_to_bs_type = ele_to_bs_type
        self.path = path
        self.dirname = '/geo_opt/' + dirname
        self.basis_arrays = []
        self.if_bs_change = if_bs_change

    def write_basis_set_all_metal(self):
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('BASISSET' + '\n')
            f.write('POB-TZVP' + '\n')

    def get_non_metal_bs_default(self, element):
        bs_ahlrichs = read_basis_set_file(element, 'Ahlrichs_VTZ')
        #bs_ahlrichs = transfer_crystal_formatted_bs_input(bs_ahlrichs)
        bs_cc = read_basis_set_file(element, 'cc-PVTZ')
        #bs_cc = transfer_crystal_formatted_bs_input(bs_cc)
        bs_combine = []
        for shell_ahl in bs_ahlrichs:
            #print(shell_ahl)
            if shell_ahl[0][0] == 'S' or shell_ahl[0][0] == 'SP' or shell_ahl[0][0] == 'P':
                bs_combine.append(shell_ahl)
        for shell_cc in bs_cc:
            if shell_cc[0][0] == 'D' or shell_cc[0][0] == 'F':
                bs_combine.append(shell_cc)
        #print(bs_combine)
        return bs_combine

    def write_basis_arrays(self):
        ele_shell_number = self.cal_shell_number()
        i = 0
        #print(self.basis_arrays)
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            for element in self.basis_arrays:
                f.write(str(ele_shell_number[i][0]) + ' ' + str(ele_shell_number[i][1]) + '\n')
                for shell in element:
                    for line in shell:
                        for unit in line:
                            f.write(str(unit) + ' ')
                        f.write('\n')
                i += 1
            f.write('99' + ' ' + '0' + '\n')

    def cal_shell_number(self):
        ele_shell_numbers = []
        ele_bs = dict(zip(list(self.ele_to_bs_type.keys()), self.basis_arrays))
        for key, value in ele_bs.items():
            #print(key)
            #print(value)
            ele_shell_number = [key, len(value)]
            ele_shell_numbers.append(ele_shell_number)
        return ele_shell_numbers

    def write_basis_set(self):
        bs_array = []
        if self.if_bs_change == 0:
            bs_type = 'POB-TZVP'
            #all metal elements with default basis set type
            #print(self.ele_to_bs_type.values())
            #print(['AHLRICHS'] * len(self.ele_to_bs_type.values()))
            if list(self.ele_to_bs_type.values()) == [bs_type] * len(self.ele_to_bs_type.values()):
                self.write_basis_set_all_metal()
            #elements of metal and non-metal with default basis set type
            elif 'POB-TZVP' in self.ele_to_bs_type.values():
                for key, value in self.ele_to_bs_type.items():
                    if value == 'POB-TZVP':
                        del self.ele_to_bs_type[key]
                with open(self.path + self.dirname + '/INPUT', 'a') as f:
                    f.write('BASISSET' + '\n')
                    f.write('POB-TZVP' + '\n')
                if len(self.ele_to_bs_type) != 0:
                    for key in self.ele_to_bs_type.keys():
                        bs_array = self.get_non_metal_bs_default(key)
                        self.basis_arrays.append(bs_array)
                    self.basis_arrays = transfer_crystal_formatted_bs_input(self.basis_arrays, self.ele_to_bs_type.keys())
                    self.write_basis_arrays()
            #all non-metal elements with default basis set type
            elif list(self.ele_to_bs_type.values()) == ['AHLRICHS'] * len(self.ele_to_bs_type.values()):
                for key in self.ele_to_bs_type.keys():
                    #print(key)
                    bs_array = self.get_non_metal_bs_default(key)
                    self.basis_arrays.append(bs_array)
                self.basis_arrays = transfer_crystal_formatted_bs_input(self.basis_arrays, self.ele_to_bs_type.keys())
                self.write_basis_arrays()
        else:
            for key,value in self.ele_to_bs_type.items():
                bs_array = read_basis_set_file(key, value)
                #print(bs_array)
                self.basis_arrays.append(bs_array)
            #print(self.basis_arrays)
            self.basis_arrays = transfer_crystal_formatted_bs_input(self.basis_arrays, self.ele_to_bs_type.keys())
            #print(self.basis_arrays)
            self.write_basis_arrays()
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('END' + '\n')


class Cal_Input(object):

    def __init__(self, path, elements, dirname, functional = 'PBE0'):
        self.elements = elements
        self.method_type = 'PBE0'
        self.path = path
        self.dirname = '/geo_opt/' + dirname
        self.functional = functional

    def write_functional(self):
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('DFT' + '\n')
            if self.functional in Functionals.functionals:
                self.functional = Functionals.functionals[self.functional]
            f.write(self.functional + '\n')
            f.write('XLGRID' + '\n')
            f.write('END' + '\n')

    def write_grimme_dispersion(self):
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('GRIMME' + '\n')
            f.write('1.05' + ' ' + '20.' +  ' ' + '25.' + '\n')
            self.elements.sort()
            f.write(str(len(self.elements)) + '\n')
            for element in self.elements:
                f.write(str(element) + ' ')
                element = int(element)
                f.write(str(Grimme_parameter.C6[element]) + ' ')
                f.write(str(Grimme_parameter.R0[element]))
                f.write('\n')

    def write_other_info(self):
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('SHRINK' + '\n')
            f.write('8' + ' ' + '8' + '\n')
            f.write('TOLINTEG' + '\n')
            f.write('8' + ' ' + '8' + ' ' + '8' + ' ' + '20' + ' ' + '50' + '\n')
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
        with open(self.path + self.dirname + '/INPUT', 'a') as f:
            f.write('GUESSP' + '\n')

    def write_cal_input_init(self):
        self.write_functional()
        self.write_grimme_dispersion()
        self.write_other_info()
        print('INPUT file generated...')

    def write_cal_input(self):
        self.write_functional()
        self.write_grimme_dispersion()
        self.write_gussp()
        self.write_other_info()
        print('INPUT file generated...')


def generation_of_input():
    #geometry input
    Geo_Init = Initialization.Geo_Init()
    name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info = Geo_Init.initialization()
    path = os.getcwd()
    Geo_Inp = Geometry_Input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info)
    Geo_Inp.gen_input()
    #optimization input
    Opt_Inp = Opt_Input(path, number_of_atoms, geometry_info)
    Opt_Inp.write_opt_info()
    #basis set input
    Bs_Init = Initialization.Bs_Init(geometry_info)
    if_bs_change, ele_to_bs_type, elements = Bs_Init.initialization()
    Bs_Inp = Basis_Set_Input(path, ele_to_bs_type, if_bs_change)
    Bs_Inp.write_basis_set()
    #calculation input
    Cal_Init = Initialization.Cal_Init()
    functional = Cal_Init.functional_init()
    Cal_Inp = Cal_Input(path, elements, functional)

def write_input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info, ele_to_bs_type, elements, functional, dirname, if_bs_change, init = 0):
    #geometry input
    Geo_Inp = Geometry_Input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info, dirname)
    Geo_Inp.gen_input()
    #optimization input
    Opt_Inp = Opt_Input(path, number_of_atoms, geometry_info, dirname)
    Opt_Inp.write_opt_info()
    #basis set input
    Bs_Inp = Basis_Set_Input(path, ele_to_bs_type, dirname=dirname, if_bs_change=if_bs_change)
    Bs_Inp.write_basis_set()
    #calculation input
    Cal_Inp = Cal_Input(path, elements, dirname, functional)
    if init == 1:
        Cal_Inp.write_cal_input_init()
    else:
        Cal_Inp.write_cal_input()
