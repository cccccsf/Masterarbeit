#!/usr/bin/python3

import re
from HF2.generation_input_hf2 import Input
from HF2.generation_input_hf2 import read_inp
from HF1.generation_of_input import default_basis_set
from copy import deepcopy


class Layer_Inp(Input):

    def __init__(self, path):
        super(Layer_Inp, self).__init__(path)
        self.ghost = []


    def read_ghost_open(self):
        file = self.path + self.input
        with open(file) as f:
            lines = f.read()
        return lines

    def test_ghost_open(self):
        self.input = "/dummy"
        expected = "1 2 3 4 5"
        actual = self.read_ghost_open()
        assert(expected == actual)

    def read_ghost_progress(self):
        self.lines = self.lines.replace('\n', ':')
        self.lines = self.lines.replace(' ', '')
        self.lines = self.lines.split(':')
        return self.lines

    def test_read_ghost(self):
        inp = '1 \n 2 \n 3'
        self.lines = inp
        expected = ['1','2','3']
        actual = self.read_ghost_progress()
        assert(actual == expected)

    def testsuite(self):
        self.test_read_ghost()
        self.test_ghost_open()


    def read_ghost(self):
        file = self.path + '/INPUT'
        with open(file) as f:
            lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split())

        regex = 'GHOSTS.*?END'
        ghost = re.search(regex, lines).group(0)
        ghost = re.split(':', ghost.replace(': ', ':'))
        self.ghost = ghost


    def write_bs(self):
        if self.if_bs_change == 0:
            self.ele_to_bs_type, self.elements, self.if_metals= default_basis_set.gen_bs_info(self.geometry)
            #print(self.geometry)
            self.write_bs_default()
        elif self.if_bs_change == 1:
            self.write_bs_with_type()
        with open(self.new_path + '/INPUT', 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            for unit in self.ghost:
                f.write(str(unit) + '\n')


    def gen_input(self):
        self.geo_block = self.read_hf1_input()
        self.get_dist_and_disp()
        self.geometry = self.get_geometry()
        self.read_ghost()
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



def get_bs_type(path):
    z = os.path.split(path)[-1]
    path = os.path.split(path)[0]
    layer_type = 'bilayer'
    if z == 'underlayer' or z =='upperlayer':
        layer_type = z
        z = os.path.split(path)[-1]
        path  = os.path.split(path)[0]
    return type


#path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\hf_1\\x_-0.150\\z_-0.106\\upperlayer'
# Inp = Layer_Inp(path)
# Inp.read_ghost()
# Inp.gen_input()
#print(Inp.path)

