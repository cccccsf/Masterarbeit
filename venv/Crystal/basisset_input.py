#!/usr/bin/python3
import sys
from copy import deepcopy
from Data import Periodict_Table
from Basis_Set import basis_set_catalog
from Common import test_variable
from Common import choose_bs
from Common import read_pob_tzvp_bs
from Crystal import geometry_input

yes_or_no = {'Y':1, 'y':1, 'Yes':1, 'yes':1, 'N':0, 'n':0, 'No':0, 'no':0 }

class Basis_set(object):

    def __init__(self, elements, method, bs_type = 'default'):
        self.method = method
        self.bs_type = bs_type
        self.bs_types = [bs_type]
        self.elements = elements
        self.elements_unique = []
        self.if_metals = []
        self.bs_change = 0
        self.ele_bs_dict = {}
        self.basis_set = []
        self.read_bs()

    def __len__(self):
        return len(self.basis_set)

    def __getitem__(self, item):
        return self.basis_set[item]

    def __iter__(self):
        return iter(self.basis_set)

    def __repr__(self):
        string = ''
        for element in self.basis_set:
            head = element[0]
            string = string + str(head[0]) + ' ' + str(head[1]) + '\n'
            for shell in element[1:]:
                shell_head = shell[0]
                line = ''
                for unit in shell_head:
                    line += str(unit) + ' '
                line += '\n'
                string += line
                for line in shell[1:]:
                    l = ''
                    for unit in line:
                        try:
                            l += ' ' + '{: }'.format(float(unit)).ljust(16) + ' '
                        except Exception as e:
                            print(e)
                            l += ' ' + str(unit).ljust(16) + ' '
                    l += '\n'
                    string += l
        return string

    @staticmethod
    def elements_if_metal(elements):
        """
        Estimation element is metal of not, here 1 represent metal, 0 for non-metal
        :param elements: dict[element]
        :return:if_metal: dict[1/0]
        """
        if_metals = []
        for ele in elements:
            if ele in Periodict_Table.metal_rev:
                if_metals.append(1)
            else:
                if_metals.append(0)
        return if_metals

    def get_unique_elements(self):
        elements_unique = set(self.elements)
        elements_unique = list(elements_unique)
        elements_unique.sort()
        return elements_unique

    @staticmethod
    def if_bs_change(bs_type):
        bs_change = 0
        if bs_type == 'default':
            bs_change = 0
        elif bs_type.lower() in basis_set_catalog.bs_dicts:
            bs_change = 1
        else:
            print('Basis Set type not correct!')
            print('Do you want to use default basis set？'
                  'Plese enter yes/no:'
                  'If you enter no, the programm will stop.')
            while True:
                try:
                    y = input()
                    y = yes_or_no[y]
                    if y == 1:
                        bs_change = 0
                        break
                    else:
                        print('Programm exit...')
                        sys.exit()
                except Exception as e:
                    print(e)
        return bs_change

    def get_ele_bs_dict_with_bstype(self):
        if test_variable.test_bs_type(self.bs_type):
            for ele in self.elements_unique:
                self.ele_bs_dict[ele] = self.bs_type
        else:
            print('Please use the correct Basis Set type!!!')
            print('And restart the programm from the proper step.')
            sys.exit()

    def get_ele_bs_dict_default(self):
        for i in range(len(self.elements_unique)):
            if self.if_metals[i] == 1:
                self.ele_bs_dict[self.elements_unique[i]] = 'POB-TZVP'
            elif self.if_metals[i] == 0:
                self.ele_bs_dict[self.elements_unique[i]] = 'AHLRICHS'

    @staticmethod
    def read_bs_with_type(element, bs_type):
        bs = choose_bs.read_basis_set_file(element, bs_type)
        bs = choose_bs.transfer_crystal_formatted_bs_input([bs], [element])[0]
        return bs

    @staticmethod
    def read_bs_geo_opt_default_nonmetal(element):
        bs_ahlrichs = choose_bs.read_basis_set_file(element, 'Ahlrichs_VTZ')
        bs_cc = choose_bs.read_basis_set_file(element, 'cc-PVTZ')
        bs_combine = []
        for shell_ahl in bs_ahlrichs:
            if shell_ahl[0][0] == 'S' or shell_ahl[0][0] == 'SP' or shell_ahl[0][0] == 'P':
                bs_combine.append(shell_ahl)
        for shell_cc in bs_cc:
            if shell_cc[0][0] == 'D' or shell_cc[0][0] == 'F':
                bs_combine.append(shell_cc)
        bs_combine = choose_bs.transfer_crystal_formatted_bs_input([bs_combine],[element])[0]
        return bs_combine

    @staticmethod
    def read_bs_geo_opt_default_metal(element):
        head, bs = read_pob_tzvp_bs.read_pob_bs(element)
        for shell in bs:
            for j, line in enumerate(shell):
                shell[j] = line.split()
        return bs

    @staticmethod
    def read_bs_hf1_default_metal(element):
        head, bs = read_pob_tzvp_bs.read_pob_bs(element)
        bs = read_pob_tzvp_bs.transfer_to_target_bs(bs)
        return bs

    @staticmethod
    def read_bs_default(method, element, if_metal):
        if method == 'GEO_OPT':
            if if_metal == 1:
                bs = Basis_set.read_bs_geo_opt_default_metal(element)
            elif if_metal == 0:
                bs = Basis_set.read_bs_geo_opt_default_nonmetal(element)
        elif method == 'HF1':
            if if_metal == 1:
                bs = Basis_set.read_bs_hf1_default_metal(element)
            elif if_metal == 0:
                bs = Basis_set.read_bs_geo_opt_default_nonmetal(element)
        elif method == 'HF2':
            bs = Basis_set.read_bs_default('HF1', element, if_metal)
            bs = Basis_set.hf2_add_shells(bs)
        return bs

    @staticmethod
    def hf2_add_shells(bs):
        add_d = []
        add_f = []
        for shell in bs:
            if str(shell[0][1]) == '3':
                add_d.append(deepcopy(shell))
            elif str(shell[0][1]) == '4':
                add_f.append(deepcopy(shell))
        for shell in add_d:
            for i in range(1,len(shell)):
                shell[i][0] = str(float(shell[i][0])/3)
        for shell in add_f:
            for i in range(1,len(shell)):
                shell[i][0] = str(float(shell[i][0])/3)
        new_bs = bs + add_d + add_f
        return new_bs

    @staticmethod
    def get_bs_head(element, bs):
        head = []
        head.append(str(element))
        head.append(str(len(bs)))
        return head

    def read_bs(self):
        self.elements_unique = self.get_unique_elements()
        self.if_metals = self.elements_if_metal(self.elements_unique)
        self.bs_change = self.if_bs_change(self.bs_type)
        if self.bs_change == 1:
            self.get_ele_bs_dict_with_bstype()
            for key, value in self.ele_bs_dict.items():
                bs = self.read_bs_with_type(key, value)
                if self.method == 'HF2':
                    bs = self.hf2_add_shells(bs)
                head = self.get_bs_head(key, bs)
                bs.insert(0, head)
                self.basis_set.append(bs)
        else:
            self.get_ele_bs_dict_default()
            for i in range(len(self.elements_unique)):
                bs = self.read_bs_default(self.method, self.elements_unique[i], self.if_metals[i])
                head = self.get_bs_head(self.elements_unique[i], bs)
                bs.insert(0, head)
                self.basis_set.append(bs)

    def write_bs(self, path):
        with open(path, 'a') as f:
            for element in self.basis_set:
                head = element[0]
                f.write(str(head[0]) + ' ' + str(head[1]) + '\n')
                for shell in element[1:]:
                    shell_head = shell[0]
                    for unit in shell_head:
                        f.write(str(unit) + ' ')
                    f.write('\n')
                    for line in shell[1:]:
                        for unit in line:
                            try:
                                f.write(' ' + '{: }'.format(float(unit)).ljust(16) + ' ')
                            except Exception as e:
                                print(e)
                                f.write(' ' + str(unit).ljust(16) + ' ')
                        f.write('\n')

    def reset_bs(self, arg, value):
        self.__dict__[arg] = value
        self.__init__(self.elements, self.method, self.bs_type)

# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# geo = geometry_input.Geometry(path)
# elements = geo.elements
# method = 'HF1'
# bs = Basis_set([15], method)
# print(bs)
# p = path + '/assss'




