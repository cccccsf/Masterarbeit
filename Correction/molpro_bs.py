#!/usr/bin/python3
import os
import re
import HF2
from Common import ReadIni
from Common import Job
from Data import periodic_table_rev

class Molpro_Bs(object):

    def __init__(self, job, input_name='per_bas_rpa_iext1.inp'):
        self.job = job
        self.input_name = input_name
        self.input_file = os.path.join(self.job.path, self.input_name)
        self.hf2_bs = []
        self.bs_dict = {}
        self.mopro_form = ''


    def get_hf2_bs(self):

        ini_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        ini_file = os.path.join(ini_path, 'input.ini')
        ini_file = os.path.exists(ini_file)

        if ini_file:

            Ini = ReadIni(ini_path)
            name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
            bs_type, nodes, crystal_path = Ini.get_hf2_info()

            Inp = HF2.Input(self.job, name, slab_or_molecule, group, bs_type=bs_type)
            Inp.generate_bs()

        return Inp.bs


    def creat_bs_dict(self):
        bs_dict = {}
        for ele in self.hf2_bs:
            s_element, orbitals = self.extract_bs_info(ele)
            bs_dict[s_element] = orbitals
        return bs_dict


    def transfer_to_molpro_form(self):
        molpro_form = 'basis={\n'
        for ele, shells in self.bs_dict.items():
            inp = '! {:2s}'.format(ele) + '\n'
            inp_s = self.transfer_one_kind_oribital(ele, 's', shells['s'])
            inp_p = self.transfer_one_kind_oribital(ele, 'p', shells['p'])
            inp_d = self.transfer_one_kind_oribital(ele, 'd', shells['d'])
            inp_f = self.transfer_one_kind_oribital(ele, 'f', shells['f'])
            inp += inp_s + inp_p + inp_d + inp_f
            molpro_form += inp
        if self.if_add_H_bs():
            molpro_form = self.add_H_bs(molpro_form)
        molpro_form += '}\n'
        #print(molpro_form)
        return molpro_form


    def transfer_one_kind_oribital(self, element, oribtal_type, shells):
        curr_shells = [shell[1:] for shell in shells]
        exp = []
        for shell in curr_shells:
            for orbital in shell:
                exp.append(orbital[0])
        inp = '{}, {:2s}, '.format(oribtal_type, element)
        for e in exp:
            inp += str(e) + ', '
        inp = inp[:-2] + '\n'
        i = 1
        for shell in curr_shells:
            coe = []
            for orbital in shell:
                coe.append(orbital[1])
            length = len(coe)
            j = i + length - 1
            line = 'c, {}.{}, '.format(i, j)
            i = j + 1
            for c in coe:
                line += str(c) + ', '
            line = line[:-2] + '\n'
            inp += line
        return inp

    def extract_bs_info(self, ele):
        head = ele[0]
        element = head[0]
        s_element = periodic_table_rev[int(element)]
        shells = ele[1:]
        s_orbitals = [shell for shell in shells if shell[0][1] <= 1]
        p_orbitals = [shell for shell in shells if shell[0][1] == 2]
        d_orbitals = [shell for shell in shells if shell[0][1] == 3]
        f_orbitals = [shell for shell in shells if shell[0][1] == 4]
        orbitals = {'s': s_orbitals, 'p': p_orbitals, 'd': d_orbitals, 'f': f_orbitals}
        return s_element, orbitals

    def get_molpro_bs(self):

        self.hf2_bs = self.get_hf2_bs()
        self.bs_dict = self.creat_bs_dict()
        self.mopro_form = self.transfer_to_molpro_form()

    def add_H_bs(self, string):
        """
        add basis set of H
        :param string:
        :return:
        """
        line = 'spd, h, vtz; c\n'
        string += line
        return string

    def if_add_H_bs(self):
        """
        If H atom is added to the cluster and there is no H before, the basis set of H should be setted for continuing calculation.
        :return: True(if extra H is added to cluster) / False
        """
        if 'H' not in self.bs_dict and 'h' not in self.bs_dict and 1 not in self.bs_dict:
            with open(self.input_file, 'r') as f:
                text = f.read()
            reg = 'geometry=.*?.xyz\n'
            geo_file = re.search(reg, text)
            if geo_file != None:
                geo_file = geo_file.group(0)
                geo_file = geo_file[9:-1]
                geo_file = os.path.join(self.job.path, geo_file)
                with open(geo_file, 'r') as f:
                    lines = f.readlines()
                lines = [line.strip() for line in lines]
                for line in lines:
                    if line.startswith('H') or line.startswith('h') or line.startswith('1 '):
                        return True
            return False
        return False


    def write_bs(self):
        with open(self.input_file, 'r') as f:
            text = f.read()
        pattern = 'basis={.*?}\n'
        try:
            bs = re.search(pattern, text, re.M|re.S).group(0)
            new_text = text.replace(bs, self.mopro_form)
            with open(self.input_file, 'w') as f:
                f.write(new_text)
        except AttributeError as e:
            try:
                pattern = '.xyz\n'
                bs_text = '.xyz\n\n' + self.mopro_form + '\n'
                bs = re.search(pattern, text, re.M|re.S).group(0)
                new_text = text.replace(bs, bs_text)
                with open(self.input_file, 'w') as f:
                    f.write(new_text)
            except AttributeError as e:
                print(e)
                print('Add Basis Set info failed.')
                print('Please check and try again.')

