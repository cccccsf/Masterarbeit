#!/usr/bin/python3
import os
import re
import sys
from copy import deepcopy
from Common import test_variable

def read_input_file(path):
    """
    read original INPUT file into lines
    :param path: str
    :return: lines: lines of the INPUT file [line]
    """
    file_input = os.path.join(path, 'INPUT')
    f = open(file_input, 'r')
    lines = f.read().replace('\n', ':')
    f.close()
    lines = ' '.join(lines.split())   #remove whitespace
    lines = re.split(':', lines.replace(': ', ':'))
    return lines


def split_block(lines):
    sep = []
    for num, line in enumerate(lines):
        if line == 'END':
            sep.append(num)
    geo_block = lines[:(sep[0]+1)]
    bs_block= lines[(sep[0]+1):(sep[1]+1)]
    func_block = lines[(sep[1]+1):(sep[2]+1)]
    cal_block = lines[(sep[2]+1):(sep[3]+1)]
    blocks = []
    blocks.append(geo_block)
    blocks.append(bs_block)
    blocks.append(func_block)
    blocks.append(cal_block)
    return blocks


def split_geometry(geometry):
    new_geometry = []
    for atom in geometry:
        new_atom = atom.split()
        new_geometry.append(new_atom)
    return new_geometry


def split_lattice_para(lattice_para):
    new_lattice_para = lattice_para.split()
    return new_lattice_para


def read_geo_block(geo_block):
    name = geo_block[0]
    slab_or_molecule = geo_block[1]
    group = geo_block[2]
    lattice_para = geo_block[3]
    lattice_para = split_lattice_para(lattice_para)
    number_of_atoms = geo_block[4]
    geometry = geo_block[5:-1]
    geometry = split_geometry(geometry)
    return name, slab_or_molecule, group, lattice_para, number_of_atoms, geometry


def read_bs_block(bs_block):
    bs_type = bs_block[0]
    return bs_type


def read_func_block(func_block):
    functional = func_block[0]
    return functional


def read_cal_block(cal_block):
    pass


def exit_programm():
    try:
        sys.exit(1)
    except:
        print('INPUT form not correct!!!')
    finally:
        print('''Programm Exit...
--------------------------------------------------------------------------------------------------------------------''')


def test_vari(slab_or_molecule, group, lattice_para, number_of_atoms, geometry, bs_type, functional):
    if bs_type == 'END':
        if_bs_change = 0
    else:
        if_bs_change = 1
    if not test_variable.test_slab_or_molecule(slab_or_molecule):
        print('''
slab or molecule not correct!!!
Please correct!!!''')
        exit_programm()
    elif not test_variable.test_group(group, slab_or_molecule):
        print('''
group type not correct!!!
Please correct!!!''')
        exit_programm()
    elif not test_variable.test_lattice_parameter(lattice_para, slab_or_molecule):
        print('''lattice parameter not correct!!!
Please correct!!!''')
        exit_programm()
    elif not test_variable.test_geometry(number_of_atoms, geometry, slab_or_molecule):
        #print(len(geometry))
        print('geometry:')
        print(geometry)
        print('''
geometry not correct!!!
Please correct!!!''')
        exit_programm()
    elif if_bs_change == 1:
        if not test_variable.test_bs_type(bs_type):
            print(bs_type)
            print('''
basis set type not correct!!!
Please correct!!!''')
            exit_programm()
    elif not test_variable.test_functional(functional):
        print('')
        print('''
functional type "{0}" not correct!!!
Please correct!!!'''.format(functional))
        exit_programm()


def read_input(path):
    lines = read_input_file(path)
    blocks = split_block(lines)
    name, slab_or_molecule, group, lattice_para, number_of_atoms, geometry = read_geo_block(blocks[0])
    bs_type = read_bs_block(blocks[1])
    functional = read_func_block(blocks[2])
    test_vari(slab_or_molecule, group, lattice_para, number_of_atoms, geometry, bs_type, functional)
    return name, slab_or_molecule, group, lattice_para, number_of_atoms, geometry, bs_type, functional


