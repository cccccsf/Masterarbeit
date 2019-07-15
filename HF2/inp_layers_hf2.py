#!/usr/bin/python3
import os
import re
from HF2 import Input
from copy import deepcopy
from Crystal import Basis_set


class Layer_Inp(Input):

    def __init__(self, hf1_job, name, slab_or_molecule, layer_group, layertype, bs_type='default', fixed_atoms=[], cal_parameters={}, aos=0):
        super(Layer_Inp, self).__init__(hf1_job, name, slab_or_molecule, layer_group, bs_type, layertype=layertype, fixed_atoms=fixed_atoms, cal_parameters=cal_parameters, aos=aos)
        self.ghost = self.read_ghost()

    def read_ghost(self):
        file = self.hf1_job.path + '/INPUT'
        with open(file) as f:
            lines = f.read().replace('\n', ':')
        lines = ' '.join(lines.split())

        regex = 'GHOSTS.*?END'
        ghost = re.search(regex, lines).group(0)
        ghost = re.split(':', ghost.replace(': ', ':'))
        return ghost

    def write_bs(self):
        if self.aos == 0:
            self.bs = Basis_set(self.geometry.elements, 'HF2', self.bs_type)
        else:
            self.bs = Basis_set(self.geometry.elements, 'HF1', self.bs_type, self.aos)
        self.bs.write_bs(self.input_path)
        if self.aos != 0:
            with open(self.input_path, 'a') as f:
                for ao in self.aos:
                    f.write(ao + '\n')
        with open(self.input_path, 'a') as f:
            f.write('99' + ' ' + '0' + '\n')
            for unit in self.ghost:
                f.write(str(unit) + '\n')
            f.write('END' + '\n')



