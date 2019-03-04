#!/usr/bin/python3
import os
from configparser import ConfigParser
from Common import test_variable


class ReadIni(object):

    def __init__(self, path):
        self.ini_path = path
        self.cfg = ConfigParser()

        self.project_path = ''
        self.start = ''
        self.end = ''

        self.project_name = ''
        self.system_type = 'SLAB'
        self.group_type = 1
        self.lattice_parameter = []
        self.number_atoms = 0
        self.geometry = []
        self.fixed_atoms = []

        self.bs_geo_opt = ''
        self.functional = ''
        self.nodes_geo_opt = 12
        self.crystal_path = ''

        self.bs_hf1 = ''
        self.nodes_hf1 = 12

        self.bs_hf2 = ''
        self.nodes_hf2 = 12

        self.nodes_loc = 1

        self.nodes_lmp2 = 1
        self.cryscor_path = ''

        self.nodes_rpa_b = 1
        self.nodes_rpa_s = 28
        self.molpro_key = ''
        self.molpro_path = ''

        self.read_ini_file()
        #self.test_parameters()


    def read_ini_file(self):
        try:
            ini_path = os.path.join(self.ini_path, 'input.ini')
            self.cfg.read(ini_path, encoding='utf-8')

            self.project_path = self.cfg.get('Initilization', 'path')
            self.start = self.cfg.get('Initilization', 'start')
            self.end = self.cfg.get('Initilization', 'end')

            self.project_name = self.cfg.get('Basic_Info', 'project_name')
            self.system_type = self.cfg.get('Basic_Info', 'system_type')
            self.group_type = self.cfg.getint('Basic_Info', 'group_type')
            self.lattice_parameter = self.read_lattice_parameter()
            self.number_atoms = self.cfg.getint('Basic_Info', 'number_of_atoms')
            self.geometry = self.read_geometry()
            self.fixed_atoms = self.read_fixed_atoms()
        except Exception as e:
            print(e)


    def read_lattice_parameter(self):
        lp = self.cfg.get('Basic_Info', 'lattice_parameter')
        lp = lp.split()
        lp = [float(l) for l in lp]
        length = []
        angle = []
        if len(lp) == 6:
            length = lp[:3]
            angle = lp[3:]
        elif len(lp) == 3 and lp[-1] >25:
            length = lp[:2]
            angle = lp[2:]
        else:
            length = [l for l in lp if l <= 25]
            angle = [l for l in lp if l > 25]
        new_lp = []
        new_lp.append(length)
        new_lp.append(angle)
        return new_lp


    def if_none(self, value):
        if value == '' or value == None:
            return 'default'
        else:
            return value


    def read_geometry(self):
        basic_info_para = self.cfg.options('Basic_Info')
        geoParas = [para for para in basic_info_para if para.startswith('geometry')]
        geoLines = [self.cfg.get('Basic_Info', geoPara) for geoPara in geoParas]
        geometry = [geoline.split() for geoline in geoLines]
        return geometry

    def read_fixed_atoms(self):
        fixed_atoms = self.cfg.get('Basic_Info', 'fixed_atoms')
        fixed_atoms = fixed_atoms.split()
        return fixed_atoms

    def get_initialization_info(self):
        return self.project_path, self.start, self.end

    def get_basic_info(self):
        return self.project_name, self.system_type, self.group_type, self.lattice_parameter, self.number_atoms, self.fixed_atoms

    def get_geometry(self):
        return self.geometry

    def get_geo_opt_info(self):
        self.bs_geo_opt = self.cfg.get('Geo_Opt', 'basis_set')
        self.bs_geo_opt = self.if_none(self.bs_geo_opt)
        self.functional = self.cfg.get('Geo_Opt', 'functional')
        self.functional = self.if_none(self.functional)
        if self.functional == 'default' or self.functional == '':
            self.functional = 'PBE0'
        self.nodes_geo_opt = self.cfg.get('Geo_Opt', 'nodes')
        self.crystal_path = self.cfg.get('Geo_Opt', 'crystal_path')
        return self.bs_geo_opt, self.functional, self.nodes_geo_opt, self.crystal_path


    def get_hf1_info(self):
        self.bs_hf1 = self.cfg.get('HF1', 'basis_set')
        self.bs_hf1 = self.if_none(self.bs_hf1)
        self.nodes_hf1 = self.cfg.get('HF1', 'nodes')
        return self.bs_hf1, self.nodes_hf1, self.crystal_path


    def get_hf2_info(self):
        self.bs_hf2 = self.cfg.get('HF2', 'basis_set')
        self.bs_hf2 = self.if_none(self.bs_hf2)
        self.nodes_hf2 = self.cfg.get('HF1', 'nodes')
        return self.bs_hf2, self.nodes_hf2, self.crystal_path


    def get_loc_info(self):
        self.nodes_loc = self.cfg.get('Localization', 'nodes')
        return self.nodes_loc, self.crystal_path


    def get_lmp2_info(self):
        self.nodes_lmp2 = self.cfg.get('LMP2', 'nodes')
        self.cryscor_path = self.cfg.get('LMP2', 'cryscor_path')
        return self.nodes_lmp2, self.cryscor_path


    def get_rpa_info(self):
        self.nodes_rpa_b = self.cfg.get('RPA', 'bilayer_nodes')
        self.nodes_rpa_s = self.cfg.get('RPA', 'singlelayer_nodes')
        self.molpro_key = self.cfg.get('RPA', 'molpro_KEY')
        self.molpro_path = self.cfg.get('RPA', 'molpro_path')
        return self.nodes_rpa_b, self.nodes_rpa_s, self.molpro_key, self.molpro_path


    def get_cluster_info(self):
        size = self.cfg.get('Cluster', 'size')
        size = size.upper()
        center_atoms = self.cfg.get('Cluster', 'center_atoms')
        center_atoms = self.split_atoms(center_atoms)
        upper_center_atoms = self.cfg.get('Cluster', 'upper_center_atoms')
        under_center_atoms = self.cfg.get('Cluster', 'under_center_atoms')
        upper_center_atoms = self.split_atoms(upper_center_atoms)
        under_center_atoms = self.split_atoms(under_center_atoms)
        center_atoms = self.process_center_atoms(center_atoms, upper_center_atoms, under_center_atoms)
        factors_upper = self.cfg.get('Cluster', 'upper_center_atoms')
        factors_upper = self.split_factors(factors_upper)
        factors_under = self.cfg.get('Cluster', 'under_center_atoms')
        if factors_under != '':
            factors_under = factors_upper
        factors_under = self.split_factors(factors_under)
        factors = [factors_upper, factors_under]
        return size, center_atoms, factors

    def split_atoms(self, atoms):
        if atoms == '' or atoms == None:
            atoms = []
        else:
            atoms = atoms.split()
        return atoms

    def split_factors(self, factors):
        try:
            factors = factors.split()
            factors = [float(fac) for fac in factors]
        except Exception as e:
            print(e)
        return factors

    def process_center_atoms(self, atoms, upper_atoms, under_atoms):
        if upper_atoms != [] and under_atoms != []:
            atoms = [upper_atoms, under_atoms]
        return atoms


    def test_parameters(self):
        if not test_variable.test_slab_or_molecule(self.system_type):
            print('''
    slab or molecule not correct!!!
    Please correct!!!''')
            exit_programm()
        elif not test_variable.test_group(self.group_type, self.system_type):
            print('''
    Group type not correct!!!
    Please correct!!!''')
            exit_programm()
        elif not test_variable.test_lattice_parameter(self.lattice_parameter, self.system_type):
            print('''
    Lattice parameter not correct!!!
    Please correct!!!''')
            exit_programm()
        elif not test_variable.test_geometry(self.number_atoms, self.geometry, self.system_type):
            print('geometry:')
            print(geometry)
            print('''
    geometry not correct!!!
    Please correct!!!''')
            exit_programm()
        elif self.bs_geo_opt != 'default':
            if not test_variable.test_bs_type(self.bs_geo_opt):
                print(self.bs_geo_opt)
                print('''
    basis set type not correct!!!
    Please correct!!!''')
                exit_programm()
        elif not test_variable.test_functional(self.functional):
            print('')
            print('''
    functional type "{0}" not correct!!!
    Please correct!!!'''.format(self.functional))
            exit_programm()
        elif self.bs_hf1 != 'default':
            if not test_variable.test_bs_type(self.bs_hf1):
                print(self.bs_hf1)
                print('''
    HF1 basis set type not correct!!!
    Please correct!!!''')
                exit_programm()
        elif self.bs_hf2 != 'default':
            if not test_variable.test_bs_type(self.bs_hf2):
                print(self.bs_hf2)
                print('''
    HF2 basis set type not correct!!!
    Please correct!!!''')
                exit_programm()



def exit_programm():
    try:
        sys.exit(1)
    except:
        print('INPUT form not correct!!!')
    finally:
        print('''
        Programm Exit...
    --------------------------------------------------------------------------------------------------------------------''')




def test_read_ini():
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    Ini = ReadIni(path)
    Ini.read_fixed_atoms()


#test_read_ini()
