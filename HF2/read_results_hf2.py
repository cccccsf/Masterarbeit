#!/usr/bin/python3
import re
from Common import read_all_results
from Common import Job


def get_energy(path):
    if isinstance(path, Job):
        path = path.path
    f = open(path + '/hf2.out', 'r')
    lines = f.read()
    # lines = ' '.join(lines.split()) + '#'
    f.close()

    regex = 'CYC   0.*?\n'
    # CYC   0 ETOT(AU) -2.726040216969E+03 DETOT -2.73E+03 tst  0.00E+00 PX
    # 1.00E+00
    energy_block = re.search(regex, lines).group(0)
    regex_2 = r'ETOT\(AU\) .*? '
    energy_block = re.search(regex_2, energy_block).group(0)  # ETOT(AU) -2.726040216969E+03
    unit = search_unit(energy_block)
    energy_block = energy_block.strip()
    energy_block = energy_block.split(' ')
    energy = energy_block[-1]  # str

    return energy, unit


def search_unit(energy_block):
    reg = r'\(.*?\)'
    unit_block = re.search(reg, energy_block)
    if unit_block is not None:
        unit_block = unit_block.group(0)
        unit = unit_block[1:-1]
        if unit == 'AU':
            unit = 'hartree'
    else:
        unit = 'default'
    return unit


def test_get_energy():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106'
    energy = get_energy(path)
    expected = '-2.726040216969E+03'
    assert(energy == expected)


def read_all_results_hf2(jobs, init_dist=3.1):
    read_all_results(
        jobs,
        'hf2',
        energy_func=get_energy,
        init_distance=init_dist)
