#!/usr/bin/python3
import os
import sys
from Common import test_variable


class Read_input(object):

    def __init__(self, path):
        self.path = path
        self.input_file = ''
        self.blocks = []

        self.name = ''
        self.slab_or_molecule = ''
        self.group = ''
        self.lattice_parameter = []
        self.number_of_atoms = 0
        self.geometry = []
        self.bs_type = ''
        self.functional = ''

        self.hf1_bs = ''
        self.hf2_bs = ''


        self.get_all_values()
        self.test_parameters()


    def read_input_file(self):
        path = os.path.join(self.path, 'INPUT')
        with open(path, 'r') as f:
            self.input_file = f.read()

    def transfer_input(self):
        self.read_input_file()
        inp = self.input_file
        inp = inp.split('\n')

        inp_without_comment = []
        for line in inp:
            i = 0
            for c in line:
                position = -1
                if c == '#':
                    position = i
                    break
                i += 1
            new_line = line[:position]
            inp_without_comment.append(new_line)

        for i in range(len(inp_without_comment)):
            inp_without_comment[i] = inp_without_comment[i].strip()

        return inp_without_comment


    def input_split(self):
        inp_without_comment = self.transfer_input()
        sep = []
        for num, line in enumerate(inp_without_comment):
            if line == 'END':
                sep.append(num)
        geo_block = inp_without_comment[:(sep[0]+1)]
        bs_block= inp_without_comment[(sep[0]+1):(sep[1]+1)]
        func_block = inp_without_comment[(sep[1]+1):(sep[2]+1)]
        cal_block = inp_without_comment[(sep[2]+1):(sep[3]+1)]
        hf1_block = inp_without_comment[(sep[3]+1):(sep[4]+1)]
        hf2_block = inp_without_comment[(sep[4]+1):(sep[5]+1)]
        blocks = []
        blocks.append(geo_block)
        blocks.append(bs_block)
        blocks.append(func_block)
        blocks.append(cal_block)
        blocks.append(hf1_block)
        blocks.append(hf2_block)
        return blocks

    @staticmethod
    def split_geometry(geometry):
        new_geometry = []
        for atom in geometry:
            new_atom = atom.split()
            new_geometry.append(new_atom)
        return new_geometry

    @staticmethod
    def split_lattice_para(lattice_para):
        new_lattice_para = lattice_para.split()
        return new_lattice_para

    def read_geo_block(self):
        geo_block = self.blocks[0]
        self.name = geo_block[0]
        self.slab_or_molecule = geo_block[1]
        self.group = geo_block[2]
        lattice_para = geo_block[3]
        self.lattice_parameter = self.split_lattice_para(lattice_para)
        self.number_of_atoms = geo_block[4]
        geometry = geo_block[5:-1]
        self.geometry = self.split_geometry(geometry)

    def read_bs_block(self):
        bs_block = self.blocks[1]
        if len(bs_block) == 2:
            if bs_block[0] != '':
                self.bs_type = bs_block[0]
            else:
                self.bs_type = 'default'
        else:
            self.bs_type = 'default'

    def read_functional(self):
        func_block = self.blocks[2]
        if len(func_block) == 2:
            if func_block[0] != '':
                self.functional = func_block[0]
            else:
                self.bs_type = 'PBE0'
        else:
            self.bs_type = 'PBE0'

    def read_hf1(self):
        hf1_block = self.blocks[4]
        if len(hf1_block) == 2:
            if hf1_block[0] != '':
                self.hf1_bs = hf1_block[0]
            else:
                self.hf1_bs = 'default'
        else:
            self.hf1_bs = 'default'

    def read_hf2(self):
        hf2_block = self.blocks[5]
        if len(hf2_block) == 2:
            if hf2_block[0] != '':
                self.hf2_bs = hf2_block[0]
            else:
                self.hf2_bs = 'default'
        else:
            self.hf2_bs = 'default'

    def get_all_values(self):
        self.blocks = self.input_split()
        self.read_geo_block()
        self.read_bs_block()
        self.read_functional()
        self.read_hf1()
        self.read_hf2()

    def test_parameters(self):
        if not test_variable.test_slab_or_molecule(self.slab_or_molecule):
            print('''
    slab or molecule not correct!!!
    Please correct!!!''')
            exit_programm()
        elif not test_variable.test_group(self.group, self.slab_or_molecule):
            print('''
    Group type not correct!!!
    Please correct!!!''')
            exit_programm()
        elif not test_variable.test_lattice_parameter(self.lattice_parameter, self.slab_or_molecule):
            print('''
    Lattice parameter not correct!!!
    Please correct!!!''')
            exit_programm()
        elif not test_variable.test_geometry(self.number_of_atoms, self.geometry, self.slab_or_molecule):
            print('geometry:')
            print(geometry)
            print('''
    geometry not correct!!!
    Please correct!!!''')
            exit_programm()
        elif self.bs_type != 'default':
            if not test_variable.test_bs_type(self.bs_type):
                print(self.bs_type)
                print('''
    basis set type not correct!!!
    Please correct!!!''')
                exit_programm()
        elif not test_variable.test_functional(self.functional):
            print('')
            print('''
    functional type "{0}" not correct!!!
    Please correct!!!'''.format(self.functional))
            exit_programm()
        elif self.hf1_bs != 'default':
            if not test_variable.test_bs_type(self.hf1_bs):
                print(self.hf1_bs)
                print('''
    HF1 basis set type not correct!!!
    Please correct!!!''')
                exit_programm()
        elif self.hf2_bs != 'default':
            if not test_variable.test_bs_type(self.hf2_bs):
                print(self.hf2_bs)
                print('''
    HF2 basis set type not correct!!!
    Please correct!!!''')
                exit_programm()


def test_transfer(Inp):
    inp_without_comment = Inp.transfer_input()
    expectet = ['black p', 'SLAB', '1', '3.27 4.36 90', '8', '15     -2.500000000000E-01 -4.213700000000E-01  3.700000000000E+0', '15      2.500000000000E-01 -7.863000000000E-02  3.700000000000E+0', '15      2.500000000000E-01  7.863000000000E-02  1.550000000000E+0', '15     -2.500000000000E-01  4.213700000000E-01  1.550000000000E+0', '15      2.500000000000E-01 -4.213700000000E-01 -1.550000000000E+0', '15     -2.500000000000E-01 -7.863000000000E-02 -1.550000000000E+0', '15     -2.500000000000E-01  7.863000000000E-02 -3.700000000000E+0', '15      2.500000000000E-01  4.213700000000E-01 -3.700000000000E+0', 'END', '', 'END', 'PBE0', 'END', 'END', 'cc-pvtz', 'END', 'cc-pvtz', 'END']
    assert(inp_without_comment == inp_without_comment)

def test_split(Inp):
    blocks = Inp.input_split()
    expected = [['black p', 'SLAB', '1', '3.27 4.36 90', '8', '15     -2.500000000000E-01 -4.213700000000E-01  3.700000000000E+0', '15      2.500000000000E-01 -7.863000000000E-02  3.700000000000E+0', '15      2.500000000000E-01  7.863000000000E-02  1.550000000000E+0', '15     -2.500000000000E-01  4.213700000000E-01  1.550000000000E+0', '15      2.500000000000E-01 -4.213700000000E-01 -1.550000000000E+0', '15     -2.500000000000E-01 -7.863000000000E-02 -1.550000000000E+0', '15     -2.500000000000E-01  7.863000000000E-02 -3.700000000000E+0', '15      2.500000000000E-01  4.213700000000E-01 -3.700000000000E+0', 'END'], ['', 'END'], ['PBE0', 'END'], ['END'], ['cc-pvtz', 'END'], ['cc-pvtz', 'END']]
    assert(blocks == expected)

def test_split_geometry():
    geometry = '15     -2.500000000000E-01 -4.213700000000E-01  3.700000000000E+0', '15      2.500000000000E-01 -7.863000000000E-02  3.700000000000E+0', '15      2.500000000000E-01  7.863000000000E-02  1.550000000000E+0', '15     -2.500000000000E-01  4.213700000000E-01  1.550000000000E+0', '15      2.500000000000E-01 -4.213700000000E-01 -1.550000000000E+0', '15     -2.500000000000E-01 -7.863000000000E-02 -1.550000000000E+0', '15     -2.500000000000E-01  7.863000000000E-02 -3.700000000000E+0', '15      2.500000000000E-01  4.213700000000E-01 -3.700000000000E+0'
    new_geometry = Read_input.split_geometry(geometry)
    expected = [['15', '-2.500000000000E-01', '-4.213700000000E-01', '3.700000000000E+0'], ['15', '2.500000000000E-01', '-7.863000000000E-02', '3.700000000000E+0'], ['15', '2.500000000000E-01', '7.863000000000E-02', '1.550000000000E+0'], ['15', '-2.500000000000E-01', '4.213700000000E-01', '1.550000000000E+0'], ['15', '2.500000000000E-01', '-4.213700000000E-01', '-1.550000000000E+0'], ['15', '-2.500000000000E-01', '-7.863000000000E-02', '-1.550000000000E+0'], ['15', '-2.500000000000E-01', '7.863000000000E-02', '-3.700000000000E+0'], ['15', '2.500000000000E-01', '4.213700000000E-01', '-3.700000000000E+0']]
    assert(expected == new_geometry)

def test_split_lattice_parameter():
    lattice_para = '3.27 4.36 90'
    new_lattice_para = Read_input.split_lattice_para(lattice_para)
    expected = ['3.27', '4.36', '90']
    assert(expected == new_lattice_para)

def test_read_geoblock(inp):
    inp.read_geo_block()
    name_expected = 'black p'
    m_s_expected = 'SLAB'
    group_expected = '1'
    number_atoms_expected = '8'
    name = inp.name
    m_s = inp.slab_or_molecule
    group = inp.group
    number_atoms = inp.number_of_atoms
    assert(name == name_expected)
    assert(m_s_expected == m_s)
    assert(group_expected == group)
    assert(number_atoms_expected == number_atoms)

def test_read_bs(inp):
    inp.read_bs_block()
    expected = 'default'
    bs_type = inp.bs_type
    assert(expected == bs_type)
	
def test_read_functional(inp):
	inp.read_functional()
	excepted = 'PBE0'
	functional = inp.functional
	assert(excepted == functional)

def test_read_hf1(inp):
    inp.read_hf1()
    expected = 'cc-pvtz'
    hf1_bs = inp.hf1_bs
    assert(expected == hf1_bs)

def test_read_hf2(inp):
    inp.read_hf2()
    expected = 'cc-pvtz'
    hf2_bs = inp.hf2_bs
    assert(hf2_bs == expected)



def test_Read_input():
    path = os.path.dirname(__file__)
    path = os.path.join(path, 'Test_file')
    inp = Read_input(path)
    inp.read_input_file()

    test_transfer(inp)
    test_split(inp)
    test_split_geometry()
    test_split_lattice_parameter()
    test_read_geoblock(inp)
    test_read_bs(inp)
    test_read_functional(inp)

    test_read_hf1(inp)
    test_read_hf2(inp)



#test_Read_input()



def exit_programm():
    try:
        sys.exit(1)
    except:
        print('INPUT form not correct!!!')
    finally:
        print('''
        Programm Exit...
    --------------------------------------------------------------------------------------------------------------------''')



