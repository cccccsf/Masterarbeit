#!/usr/bin/python3
from Data import Periodict_Table

def gen_element(geometry):
    elements = []

    for atom in geometry:
        if type(atom) == str:
            element  = atom.split(' ')[0]
        elif type(atom) == list:
            element = atom[0]
        elements.append(element)
    elements = set(elements)
    elements = list(elements)
    elements.sort()
    return elements    #z. B. [6, 16, 15, 26]  ##['C', 'S', 'P', 'Fe']


def if_metal(elements):
    metal = 0
    if_metals = []
    for ele in elements:
        if ele in Periodict_Table.metal_rev:
            metal = 1
            if_metals.append(metal)
        else:
            metal = 0
            if_metals.append(metal)
    #z. B. if_metals = [0, 0, 0, 1]
    return if_metals


def bs_type_default(if_metals):
    count = 0
    bs_types = []
    type = 'POB-TZVP'
    for i in if_metals:
        if i == 1:
            type = 'POB-TZVP'
            bs_types.append(type)
        elif i == 0:
            type ='AHLRICHS'
            bs_types.append(type)
    #z. B. bs_types = ['AHLRICHS', 'AHLRICHS', 'AHLRICHS', 'POB-TZVP']
    return bs_types

#generation of the dict of the atomic number to basis set type
def gen_num_bs(elements, bs_types):
    i = 0
    ele_to_bs_type = {}
    for ele in elements:
        ele_to_bs_type[ele] = bs_types[i]
        i += 1
    #z. B. num_bs_types = {6: 'AHLRICHS', 16: 'AHLRICHS', 15: 'AHLRICHS', 26: 'POB-TZVP'}
    return  ele_to_bs_type


def gen_bs_info(geometry):
    elements = gen_element(geometry)
    if_metals = if_metal(elements)
    bs_types = bs_type_default(if_metals)
    ele_to_bs_type = gen_num_bs(elements, bs_types)
    return ele_to_bs_type, elements, if_metals
