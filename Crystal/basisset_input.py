#!/usr/bin/python3
import sys
from copy import deepcopy
from Data import Periodict_Table
from Basis_Set import basis_set_catalog
from Common import test_variable
from Common import choose_bs
from Common import read_pob_tzvp_bs

yes_or_no = {'Y': 1, 'y': 1, 'Yes': 1, 'yes': 1, 'N': 0, 'n': 0, 'No': 0, 'no': 0 }


class Basis_set(object):

    def __init__(self, elements, method, bs_type='default', aos=0):
        self.method = method
        self.bs_type = bs_type
        self.bs_types = [bs_type]
        self.elements = elements
        self.elements_unique = []
        self.if_metals = []
        self.bs_change = 0
        self.ele_bs_dict = {}
        self.basis_set = []
        self.aos = aos
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
                            try:
                                u = unit.replace('D', 'E', 1)
                                l += ' ' + '{: }'.format(float(u)).ljust(16) + ' '
                            except Exception as er:
                                print(e)
                                print(er)
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
    def read_bs_geo_opt_default_nonmetal(element, method='HF1'):
        bs_ahlrichs = choose_bs.read_basis_set_file(element, 'Ahlrichs_VTZ')
        bs_cc = choose_bs.read_basis_set_file(element, 'cc-pVTZ')
        bs_combine = []
        for shell_ahl in bs_ahlrichs:
            if shell_ahl[0][0] == 'S' or shell_ahl[0][0] == 'SP' or shell_ahl[0][0] == 'P':
                bs_combine.append(shell_ahl)
        if method == 'HF1':
            for shell_cc in bs_cc:
                if shell_cc[0][0] == 'D' or shell_cc[0][0] == 'F':
                    bs_combine.append(shell_cc)
        elif method == 'GEO_OPT':
            for shell_cc in bs_cc:
                if shell_cc[0][0] == 'D':
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
                bs = Basis_set.read_bs_geo_opt_default_nonmetal(element, method='GEO_OPT')
        elif method == 'HF1':
            if if_metal == 1:
                bs = Basis_set.read_bs_hf1_default_metal(element)
            elif if_metal == 0:
                bs = Basis_set.read_bs_geo_opt_default_nonmetal(element, method='HF1')
        elif method == 'HF2':
            if if_metal == 1:
                bs = Basis_set.read_bs_default('HF1', element, if_metal)
                bs = Basis_set.hf2_add_shells_metal(bs)
            elif if_metal == 0:
                bs = Basis_set.read_bs_hf2_default_nonmetal(element)
        return bs

    @staticmethod
    def hf2_add_shells_metal(bs):
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
    def read_bs_hf2_default_nonmetal(element):
        bs_ahlrichs = choose_bs.read_basis_set_file(element, 'Ahlrichs_VTZ')
        bs_cc = choose_bs.read_basis_set_file(element, 'cc-pVTZ')
        bs_aug = choose_bs.read_basis_set_file(element, 'aug-cc-pVTZ')
        bs_combine = []
        ahl_s = [shell for shell in bs_ahlrichs if shell[0][0] == 'S' or shell[0][0] == 'SP']
        ahl_p = [shell for shell in bs_ahlrichs if shell[0][0] == 'P']
        cc_d = [shell for shell in bs_cc if shell[0][0] == 'D']
        cc_f = [shell for shell in bs_cc if shell [0][0] == 'F']
        aug_d = [shell for shell in bs_aug if shell[0][0] == 'D']
        aug_f = [shell for shell in bs_aug if shell[0][0] == 'F']
        bs_combine = ahl_s + ahl_p + cc_d + cc_f + aug_d[-1:] + aug_f[-1:]
        # bs_combine.append(aug_d[-1])
        # bs_combine = bs_combine + cc_f
        # bs_combine.append(aug_f[-1])
        bs_combine = choose_bs.transfer_crystal_formatted_bs_input([bs_combine],[element])[0]
        return bs_combine

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
                if self.aos == 0:
                    num_aos = 0
                else:
                    num_aos = int(len(self.aos)/2)
                head[1] = int(head[1]) + num_aos
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
                                try:
                                    u = unit.replace('D', 'E', 1)
                                    f.write(' ' + '{: }'.format(float(u)).ljust(16) + ' ')
                                except Exception as er:
                                    print(e)
                                    print(er)
                                    f.write(' ' + str(unit).ljust(16) + ' ')
                        f.write('\n')

    def reset_bs(self, arg, value):
        self.__dict__[arg] = value
        self.__init__(self.elements, self.method, self.bs_type)


if __name__ == '__main__':
    # from Crystal import geometry_input
    # from Common import ReadIni
    # Ini = ReadIni()
    # geometry = Ini.geometry
    # geo = geometry_input.Geometry(geometry=geometry)
    # elements = geo.elements
    method = 'HF1'
    bs = Basis_set([13], method)
    print(bs)




