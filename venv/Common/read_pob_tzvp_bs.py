#!/usr/bin/python3
import re
import os
from Data import Periodict_Table


def read_pob_bs(element):

    basis_array = []
    element_symbol = Periodict_Table.periodic_table_rev[int(element)]
    element = str(element)
    element_number_transfer = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06', '7': '07', '8': '08', '9': '09'}
    if element in element_number_transfer:
        element = element_number_transfer[element]

    file_input_basis = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0] + '/Basis_Set' + '/pob-TZVP' + '/{}_{}'.format(element, element_symbol)
    f = open(file_input_basis, 'r')
    lines = f.read()
    f.close()
    lines = lines.split('\n')
    if lines[-1] == '':
        lines = lines[:-1]
    head = lines[0]
    lines = lines[1:]

    input1 = input2 = []
    i = 0
    for line in lines:
        if line[0] == '0':
            if i !=0:
                input1.append(input2)
            input2 = []
            input2.append(line)
            i += 1
        else:
            input2.append(line)
    input1.append(input2)
    #print(head)
    #print(input1)
    return head, input1


def transfer_to_target_bs(bs):
    """
    for metal atoms, we use POB-tvzp BS for s, p orbitals, and 1/3 of POB-tvzp for d orbitals and 2/3 of POB-tvzp for f orbitals
    :param bs: [shell[line[unit]]]
    :return: bs: after calculation
    """

    for shell in bs:
        for j, line in enumerate(shell):
            shell[j] = line.split()

    for shell in bs:
        if shell[0][1] == '3':
            for i in range(1,len((shell))):
                shell[i][0] = str(float(shell[i][0]) / 3)
        if shell[0][1] == '4':
            for i in range(1,len((shell))):
                shell[i][0] = str(float(shell[i][0]) * (2/3))

    return bs

#head, bs0 = read_pob_bs(15)
#bs = transfer_to_target_bs(bs0)
#print(bs)
