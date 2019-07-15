#!/usr/bin/python3
import os
import shutil
import json
from Cluster import Atom
from Common import ReadIni
import HF2
from Data import periodic_table_rev


class InputRPACC(object):

    def __init__(self, job, name, memory, uc_atoms=(), basis_set=''):
        self.job = job
        self.path = job.path
        self.method = job.method
        self.name = name
        self.memory = memory
        self.input_file = self.get_input_file()
        self.geo_file = self.get_geo_file()
        self.bs = basis_set
        self.bs = self.get_bs()
        self.h_bs, self.df_bs = self.get_other_bs()
        self.atom1, self.atom2 = uc_atoms
        self.cluster = self.get_cluster()
        self.elements = self.get_elements()

    def get_input_file(self):
        return os.path.join(self.path, self.method+'.inp')

    def write_header(self):
        with open(self.input_file, 'w') as f:
            f.write('***,{}\n'.format(self.name))
            f.write('memory,{},m\n'.format(self.memory))
            f.write('gthresh,energy=1.d-8\n')
            f.write('gprint,cpu=1\n')
            f.write('\n')

    def get_geo_file(self):
        xyz_files = [file for file in os.listdir(self.path) if file.endswith('.xyz')]
        if len(xyz_files) == 1:
            xyz = xyz_files[0]
        else:
            print('There are more than one .xyz geometry file in the following directory:')
            print(self.path)
            for f in xyz_files:
                print(f)
            print('Which one do you want to choose?')
            print('Please enter the exact name of the .xyz file or you can enter 0 to use the one with latest modified time.')
            while True:
                xyz = input()
                if xyz in xyz_files:
                    break
                elif str(xyz) == '0':
                    xyz = self.get_min_mtime(xyz_files)
                    # print('xyz:', xyz)
                    break
                else:
                    print('Please enter the right name of geometry file name or 0')
        return xyz

    def write_geo_file(self):
        with open(self.input_file, 'a') as f:
            f.write('nosym;noorient;angstrom;\n')
            assert len(self.geo_file) > 0
            f.write('geometry={}\n'.format(self.geo_file))
            f.write('\n')

    def get_min_mtime(self, xyz_files):
        max_time = 0
        for file in xyz_files:
            file_path = os.path.join(self.path, file)
            mtime = os.path.getmtime(file_path)
            if mtime > max_time:
                xyz = file
                return xyz

    def get_bs(self):
        if self.bs == '':
            bs = self.method.split('_')[0]
            bs_set = {'avdz', 'avtz', 'avqz', 'per', 'periodic'}
            assert bs in bs_set
            return bs.upper()
        else:
            return self.bs.upper()

    def get_other_bs(self):
        h_bs = 'VTZ'
        df_bs = 'avtz'
        if self.bs == 'AVDZ':
            h_bs = 'VDZ'
        elif self.bs == 'AVTZ':
            h_bs = 'VTZ'
        elif self.bs == 'AVQZ':
            h_bs = 'VQZ'
            df_bs = 'avqz'
        return h_bs, df_bs

    def write_bs(self):
        with open(self.input_file, 'a') as f:
            f.write('basis={},h={}\n'.format(self.bs, self.h_bs))
            f.write('\n')

    def write_loc(self):
        with open(self.input_file, 'a') as f:
            f.write('dfit,F4EXTSIZE=700,F3EXTSIZE=1100\n')
            f.write('local,use_dist=0,keepcls=1,idist=0,loc_method=ibo,ivdist=0,interact=1,interpair=1,how_treatclswk=5\n')
            f.write('\n')

    def write_bilayer(self):
        with open(self.input_file, 'a') as f:
            # HF
            f.write('{df-hf,basis=%s;accu,12}\n' % self.df_bs)
            f.write('edim_hf(i)=energr\n')
            # lrpa
            f.write('{df-lrpa,basis=%s\n' % self.df_bs)
            f.write('local,chgfrac=0.95\n')
            at1ucell = ''
            for a in self.atom1:
                at1ucell += a + ','
            f.write('AT1UCELL,' + at1ucell[:-1] + '\n')
            at2ucell = ''
            for a in self.atom2:
                at2ucell += a + ','
            f.write('AT2UCELL,' + at2ucell[:-1] + '\n')
            f.write('}\n')
            f.write('edim_lmp2(i)=emp2-edim_hf(i)\n')
            f.write('edim_lrpa(i)=energy-edim_hf(i)\n')
            # lccsd(t)
            f.write('{df-lccsd(t),basis=%s\n' % self.df_bs)
            f.write('local,chgfrac=0.95\n')
            f.write('AT1UCELL,' + at1ucell[:-1] + '\n')
            f.write('AT2UCELL,' + at2ucell[:-1] + '\n')
            f.write('}\n')
            f.write('edim_lccsdt(i)=energy-edim_hf(i)\n')
            f.write('\n')

    def get_cluster(self):
        json_path = self.job.root_path
        json_path = os.path.join(json_path, 'cluster.json')
        with open(json_path, 'r') as f:
            data = json.load(f)
        cluster_data = data[str(self.job.coord)]['cluster']
        cluster = []
        for a in cluster_data:
            atom = Atom(a['nat'], a['x'], a['y'], a['z'], no=a['no'], type=a['type'], coor=a['coordinate number'], coor_vec=a['coordinate vector'])
            atom.layer = a['layer']
            cluster.append(atom)
        return cluster

    def get_elements(self):
        elements1 = set()
        elements2 = set()
        for atom in self.cluster:
            if int(atom.layer) == 1:
                ele = atom.element.lower()
                elements1.add(ele)
            elif int(atom.layer) == 2:
                ele = atom.element.lower()
                elements2.add(ele)
        return [elements1, elements2]

    def write_layer(self, layer):
        assert layer == 1 or layer == 2
        with open(self.input_file, 'a') as f:
            dummy_string = 'dummy,'
            for ele in self.elements[layer-1]:
                assert isinstance(ele, str)
                dummy_string += ele + str(layer) + ','
            f.write(dummy_string[:-1] + '\n')
            # HF
            f.write('{df-hf,basis=%s;accu,12}\n' % self.df_bs)
            f.write('e{}_hf(i)=energr\n'.format(layer))
            # lrpa
            f.write('{df-lrpa,basis=%s\n' % self.df_bs)
            f.write('local,chgfrac=0.95\n')
            at1ucell = 'AT1UCELL,'
            for a in self.atom1:
                if self.cluster[int(a)-1].layer != layer:
                    at1ucell += a + ','
            at2ucell = 'AT2UCELL,'
            for a in self.atom2:
                if self.cluster[int(a)-1].layer != layer:
                    at2ucell += a + ','
            f.write(at1ucell[:-1] + '\n')
            f.write(at2ucell[:-1] + '\n')
            f.write('}\n')
            f.write('e{}_lrpa(i)=energy-e{}_hf(i)\n'.format(layer, layer))
            f.write('e{}_lmp2(i)=emp2-e{}_hf(i)\n'.format(layer, layer))
            # lccsd(t)
            f.write('{df-lccsd(t),basis=%s\n' % self.df_bs)
            f.write('local,chgfrac=0.95\n')
            f.write(at1ucell[:-1] + '\n')
            f.write(at2ucell[:-1] + '\n')
            f.write('}\n')
            f.write('e{}_lccsdt(i)=energy-e{}_hf(i)\n'.format(layer, layer))
            f.write('\n')

    def write_calculation(self):
        with open(self.input_file, 'a') as f:
            f.write('\n')
            f.write('de_hf=(edim_hf-e1_hf-e2_hf)*tokcal\n')
            f.write('de_lmp2=(edim_lmp2-e1_lmp2-e2_lmp2)*tokcal\n')
            f.write('de_lrpa=(edim_lrpa-e1_lrpa-e2_lrpa)*tokcal\n')
            f.write('de_lccsdt=(edim_lccsdt-e1_lccsdt-e2_lccsdt)*tokcal\n')
            f.write('delta_de_lccsdt_rpa=de_lccsdt-de_lrpa')

    def gen_inp(self):
        self.write_header()
        self.write_geo_file()
        self.write_bs()
        self.write_loc()
        self.write_bilayer()
        self.write_layer(1)
        self.write_layer(2)
        self.write_calculation()


class InputIext1RPA(InputRPACC):

    def __init__(self, job, name, memory, uc_atoms=(), basis_set=''):
        super(InputIext1RPA, self).__init__(job, name, memory, uc_atoms, basis_set)

    def write_loc(self):
        with open(self.input_file, 'a') as f:
            f.write('dfit,F4EXTSIZE=700,F3EXTSIZE=1100\n')
            f.write('local,use_dist=0,keepcls=1,iext=1,idist=0,loc_method=ibo,ivdist=0,interact=1,interpair=1,how_treatclswk=5\n')
            f.write('\n')

    def write_bilayer(self):
        with open(self.input_file, 'a') as f:
            # HF
            f.write('{df-hf,basis=%s;accu,12}\n' % self.df_bs)
            f.write('edim_hf(i)=energr\n')
            # lrpa
            f.write('{df-lrpa,basis=%s\n' % self.df_bs)
            f.write('local,chgfrac=0.95\n')
            at1ucell = ''
            for a in self.atom1:
                at1ucell += a + ','
            f.write('AT1UCELL,' + at1ucell[:-1] + '\n')
            at2ucell = ''
            for a in self.atom2:
                at2ucell += a + ','
            f.write('AT2UCELL,' + at2ucell[:-1] + '\n')
            f.write('}\n')
            f.write('edim_lmp2(i)=emp2-edim_hf(i)\n')
            f.write('edim_lrpa(i)=energy-edim_hf(i)\n')
            f.write('\n')

    def write_layer(self, layer):
        assert layer == 1 or layer == 2
        with open(self.input_file, 'a') as f:
            dummy_string = 'dummy,'
            for ele in self.elements[layer-1]:
                assert isinstance(ele, str)
                dummy_string += ele + str(layer) + ','
            f.write(dummy_string[:-1] + '\n')
            # HF
            f.write('{df-hf,basis=%s;accu,12}\n' % self.df_bs)
            f.write('e{}_hf(i)=energr\n'.format(layer))
            # lrpa
            f.write('{df-lrpa,basis=%s\n' % self.df_bs)
            f.write('local,chgfrac=0.95\n')
            at1ucell = 'AT1UCELL,'
            for a in self.atom1:
                if self.cluster[int(a)-1].layer != layer:
                    at1ucell += a + ','
            at2ucell = 'AT2UCELL,'
            for a in self.atom2:
                if self.cluster[int(a)-1].layer != layer:
                    at2ucell += a + ','
            f.write(at1ucell[:-1] + '\n')
            f.write(at2ucell[:-1] + '\n')
            f.write('}\n')
            f.write('e{}_lrpa(i)=energy-e{}_hf(i)\n'.format(layer, layer))
            f.write('e{}_lmp2(i)=emp2-e{}_hf(i)\n'.format(layer, layer))
            f.write('\n')

    def write_calculation(self):
        with open(self.input_file, 'a') as f:
            f.write('\n')
            f.write('de_hf=(edim_hf-e1_hf-e2_hf)*tokcal\n')
            f.write('de_lmp2=(edim_lmp2-e1_lmp2-e2_lmp2)*tokcal\n')
            f.write('de_lrpa=(edim_lrpa-e1_lrpa-e2_lrpa)*tokcal\n')


class InputPerRPA(InputIext1RPA):

    def __init__(self, job, name, memory, uc_atoms=(), basis_set=''):
        super(InputPerRPA, self).__init__(job, name, memory, uc_atoms, basis_set)
        self.hf2_bs = self.get_hf2_bs()
        self.bs_dict = self.creat_bs_dict()
        self.molpro_form = self.transfer_to_molpro_form()

    def get_hf2_bs(self):
        Ini = ReadIni()
        name, slab_or_molecule, group, *_ = Ini.get_basic_info()
        bs_type, *_ = Ini.get_hf2()
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
        # print(molpro_form)
        return molpro_form

    @staticmethod
    def transfer_one_kind_oribital(element, oribtal_type, shells):
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

    @staticmethod
    def extract_bs_info(ele):
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
            for atom in self.cluster:
                if atom.element.upper() == 'H':
                    return True
        return False

    def write_bs(self):
        with open(self.input_file, 'a') as f:
            f.write(self.molpro_form)
            f.write('\n')

    def write_loc(self):
        with open(self.input_file, 'a') as f:
            f.write('dfit,F4EXTSIZE=700,F3EXTSIZE=1100\n')
            f.write('local,use_dist=0,keepcls=1,idist=0,loc_method=ibo,ivdist=0,interact=1,interpair=1,how_treatclswk=5\n')
            f.write('cfit,invsqrt=1,BASIS_MP2=avtz/mp2fit,BASIS_CCSD=avtz/mp2fit\n')
            f.write('\n')


def copy_input(job):
    ziel_path = job.path
    original_input_file = job.parameter['original_input_file']
    file_name = os.path.split(original_input_file)[-1]
    inp_to = os.path.join(ziel_path, file_name)
    job.parameter['input_file'] = inp_to
    try:
        shutil.copy(original_input_file, inp_to)
    except Exception as e:
        print(e)


def add_geometry_name(job, xyz_name=''):
    input_file = job.parameter['input_file']
    with open(input_file, 'r') as f:
        lines = f.readlines()
    ind = 0
    for i in range(len(lines)):
        if lines[i].startswith('geometry'):
            ind = i
    if xyz_name == '':
        xyz_file = get_xyz_file(job.path)
    else:
        xyz_file = xyz_name
    geo_line = 'geometry={}\n'.format(xyz_file)
    if ind != 0:
        lines[ind] = geo_line
    else:
        lines.insert(8, geo_line)
    with open(input_file, 'w') as f:
        f.writelines(lines)
    return xyz_file


def get_xyz_file(path):
    xyz_files = [file for file in os.listdir(path) if file.endswith('.xyz')]
    if len(xyz_files) == 1:
        xyz = xyz_files[0]
    else:
        print('There are more than one .xyz geometry file in the following directory:')
        print(path)
        for f in xyz_files:
            print(f)
        print('Which one do you want to choose?')
        print('Please enter the exact name of the .xyz file or you can enter 0 to use the one with latest modified time.')
        while True:
            xyz = input()
            if xyz in xyz_files:
                break
            elif str(xyz) == '0':
                xyz = get_min_mtime(path, xyz_files)
                #print('xyz:', xyz)
                break
            else:
                print('Please enter the right name of geometry file name or 0')
    return xyz


def get_min_mtime(path, xyz_files):
    max_time = 0
    for file in xyz_files:
        file_path = os.path.join(path, file)
        mtime = os.path.getmtime(file_path)
        if mtime > max_time:
            xyz = file
    return xyz


def change_memory(job):
    input_file = job.parameter['input_file']
    with open(input_file, 'r') as f:
        lines = f.readlines()
    line_mem = 'memory,{},m\n'.format(job.parameter['memory'])
    ind = 10000
    for i in range(len(lines)):
        if lines[i].startswith('memory'):
            ind = i
    if ind != 10000:
        lines[ind] = line_mem
    else:
        lines.insert(1, line_mem)
    with open(input_file, 'w') as f:
        f.writelines(lines)


def generation_input(job, xyz_name=''):
    copy_input(job)
    if xyz_name == '':
        xyz_name = add_geometry_name(job)
    else:
        add_geometry_name(job, xyz_name)
    try:
        if job.parameter['memory'] != '':
            int(job.parameter['memory'])
            change_memory(job)
    except ValueError as e:
        print('No memory info changes.')
        print('Input file keeps the original value.')
    return xyz_name



