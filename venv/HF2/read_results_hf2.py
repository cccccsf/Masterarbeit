#!/usr/bin/python3
import os
import re
from Common import read_all_results


def get_energy(path):
    f = open(path + '/hf.out', 'r')
    lines = f.read()
    #lines = ' '.join(lines.split()) + '#'
    f.close()

    regex = 'CYC   0.*?\n'
    energy_block = re.search(regex, lines).group(0)    # CYC   0 ETOT(AU) -2.726040216969E+03 DETOT -2.73E+03 tst  0.00E+00 PX  1.00E+00
    regex_2 = 'ETOT\(AU\) .*? '
    energy_block = re.search(regex_2, energy_block).group(0)    #ETOT(AU) -2.726040216969E+03
    energy_block = energy_block.strip()
    energy_block =energy_block.split(' ')
    energy = energy_block[-1]   #str

    return energy


def test_get_energy():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106'
    energy = get_energy(path)
    expected = '-2.726040216969E+03'
    assert(energy == expected)


def read_all_results_hf2(jobs, init_dist = 3.1):
    read_all_results(jobs, 'hf2', energy_func=get_energy, init_distance=init_dist)


