#!/usr/bin/python3

import re
from HF2.generation_input_hf2 import Input
from HF1.generation_of_input import default_basis_set
from copy import deepcopy
import Crystal


class Layer_Inp(Input):

    def __init__(self, hf1_job):
        super(Layer_Inp, self).__init__(hf1_job)
        self.ghost = []


    def read_ghost(self):
        file = self.hf1_path.path + '/INPUT'
        with open(file) as f:
            lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split())

        regex = 'GHOSTS.*?END'
        ghost = re.search(regex, lines).group(0)
        ghost = re.split(':', ghost.replace(': ', ':'))
        self.ghost = ghost


    def write_bs(self):
        self.bs = Crystal.Basis_set(self.geometry.elements, 'HF2', self.bs_type)
        self.bs.write_bs(self.new_path + '/INPUT')
        with open(self.new_path + '/INPUT', 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            for unit in self.ghost:
                f.write(str(unit) + '\n')
            f.write('END' + '\n')


    def gen_input(self):
        self.geo_block = self.read_hf1_input()
        self.read_ghost()
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

