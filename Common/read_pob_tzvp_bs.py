#!/usr/bin/python3
import re
import os
from copy import deepcopy
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
    for metal atoms, we use POB-tvzp BS for s, p, d orbitals, and adding 1/3 of POB-tvzp for d orbitals and 2/3 of POB-tvzp for f orbitals in HF1 additionally
    :param bs: [shell[line[unit]]]
    :return: bs: after calculation
    """

    for shell in bs:
        for j, line in enumerate(shell):
            shell[j] = line.split()

    shell_d = [shell for shell in bs if shell[0][1] == '3']
    new_bs = [shell for shell in bs if int(shell[0][1]) < 4]

    new_shells_d = []
    new_shells_f = []
    for shell in shell_d:
        new_shell_d = []
        new_shell_f = []
        new_shell_d.append(shell[0][:])
        new_shell_f.append(shell[0][:])
        for line in shell[1:]:
            new_line_d = [str(float(line[0])/3), line[1]]
            new_line_f = [str(float(line[0])*(2/3)), line[1]]
            new_shell_d.append(new_line_d)
            new_shell_f[0][1] = '4'
            new_shell_f.append(new_line_f)
        new_shells_d.append(new_shell_d)
        new_shells_f.append(new_shell_f)

    new_bs += new_shells_d
    new_bs += new_shells_f

    return new_bs

#head, bs0 = read_pob_bs(15)
#bs = transfer_to_target_bs(bs0)
#print(bs)
