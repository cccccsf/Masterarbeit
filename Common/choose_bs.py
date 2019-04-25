#!/usr/bin/python3
import re
import os
from Common.get_e_configuration import count_num_of_shells
from Common.get_e_configuration import electron_config
from Basis_Set.basis_set_catalog import bs_dicts
from Data import Periodict_Table

def read_basis_set_file(element, bs_type):
    """
    Read a Gaussian94 formatted gaussian basis set file using a list of nuclei object
    :param elment: int
    :param bs_type: str
    :return: List[Basis]
    """

    basis_array = []
    #print(element)
    element = Periodict_Table.periodic_table_rev[int(element)]

    bs_path = os.path.dirname(os.path.realpath(__file__))
    bs_path = os.path.dirname(bs_path)
    bs_path = os.path.join(bs_path, 'Basis_Set')
    bs_type = bs_type.lower()
    bs_type = bs_dicts[bs_type]
    bs_file_name = '{}.gbs'.format(bs_type)
    bs_path = os.path.join(bs_path, bs_file_name)
    f = open(bs_path, 'r')
    lines = f.read().replace('\n', ':')
    f.close()

    regex = '-' + element + ' ' + '.*?#'    #e.g. regex = -P .*?#
    lines = ' '.join(lines.split()) + '#'   #remove whitespace and add '#' for last element
    lines = re.search(regex, lines).group(0)    #return string from regex
    lines = re.split(':', lines.replace(': ', ':')) #creat list from colon separted string
    count = 0
    for line in lines:
        if line == '****':
            break
        count +=1
    lines = lines[:count]   #creat list of the bs info of a single element
    #print(lines)

    i = 0
    input1 = input2 = []
    for line in lines:
        if any(letter in line for letter in ('S ', 'SP ', 'P ', 'D ', 'F ', 'G ')):
            #print(line)
            if i == 1:
                input1.append(input2)
                input2 = [line.split()]
            else:
                i = 1
                input2 = [line.split()]
        else:
            input2.append([b for b in line.split()])
    input1.append(input2)
    basis_array = input1
    basis_array = basis_array[1:]
    #print(basis_array)

    return basis_array


def transfer_crystal_formatted_bs_input(basis_arrays, elements):
    """
    Transfer the basis set array read from Gaussian94 formattedt file to CRYSTAL formattedt INPUT
    :param basis_arrays: List[Basis]
    :return: new_ basis_array: List[Basis]
    """

    new_basis_array = basis_arrays

    #Transfer S/SP/P/D/F to 0/1/2/3/4
    for element in new_basis_array:
        for shell in element:
            if shell[0][0] == 'S':
                shell[0][0] = 0
            elif shell[0][0] == 'SP':
                shell[0][0] = 1
            elif  shell[0][0] == 'P':
                shell[0][0] = 2
            elif shell[0][0] == 'D':
                shell[0][0] = 3
            elif shell[0][0] == 'F':
                shell[0][0] = 4
            elif shell[0][0] == 'G':
                shell[0][0] = 5
            shell[0].insert(0, 0)

    #Get the electron configuration
    e_configurations = []
    e_configuration = 0
    count_shells = []
    count_shell = []
    for element in elements:
        e_configuration =electron_config(element)
        count_shell = count_num_of_shells(e_configuration)
        e_configurations.append(e_configuration)
        count_shells.append(count_shell)

    #Add CHE(formal electron charge atrributed to the shell)
    i = 0
    for element in new_basis_array:
        for shell in element:
            if shell[0][1] == 0:
                if count_shells[i][0] >= 2:
                    shell[0].insert(3, 2)
                    count_shells[i][0] -= 2
                elif count_shells[i][0] == 1:
                    shell[0].insert(3, 1)
                    count_shells[i][0] -= 1
                elif count_shells[i][0] == 0:
                    shell[0].insert(3, 0)
            elif shell[0][1] == 1:
                if (count_shells[i][0] + count_shells[i][1]) >= 8:
                    shell[0].insert(3, 8)
                    if count_shells[i][0] >= 8:
                        count_shells[i][0] -= 8
                    else:
                        num = 8 - count_shells[i][0]
                        count_shells[i][0] = 0
                        count_shells[i][1] -= num
                elif  (count_shells[i][0] + count_shells[i][1]) > 0:
                    shell[0].insert(3, (count_shells[i][0] + count_shells[i][1]))
                    count_shells[i][0] = 0
                    count_shells[i][1] = 0
                elif (count_shells[i][0] + count_shells[i][1]) == 0:
                    shell[0].insert(3, 0)
            elif shell[0][1] == 2:
                if count_shells[i][1] >= 6:
                    shell[0].insert(3, 6)
                    count_shells[i][1] -= 6
                elif count_shells[i][1] > 0:
                    shell[0].insert(3, count_shells[i][1])
                    count_shells[i][1] = 0
                elif count_shells[i][1] == 0:
                    shell[0].insert(3, 0)
            elif shell[0][1] == 3:
                if count_shells[i][2] >=10:
                    shell[0].insert(3, 10)
                    count_shells[i][2] -= 10
                elif  count_shells[i][2] > 0:
                    shell[0].insert(3, count_shells[i][2])
                    count_shells[i][2] = 0
                elif count_shells[i][2] ==0:
                    shell[0].insert(3, 0)
            elif shell[0][1] == 4:
                if count_shells[i][3] >= 14:
                    shell[0].insert(3, 14)
                    count_shells[i][3] -= 14
                elif count_shells[i][3] > 0:
                    shell[0].insert(3, count_shells[i][3])
                    count_shells[i][3] = 0
                elif count_shells[i][3] == 0:
                    shell[0].insert(3, 0)
            elif shell[0][1] == 5:
                shell[0].insert(3, 0)
        i += 1

    return new_basis_array
