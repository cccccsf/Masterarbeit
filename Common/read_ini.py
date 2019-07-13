#!/usr/bin/python3
import os
import sys
import configparser
from Common.is_number_func import is_number


class ReadIni(object):

    method_dict = {'hf2': 3, 'hf_2': 3,
              'hf_1': 1, 'hf1': 1,
              'geo_opt': 0,
              'lmp2': 4,
              'rpa': 5, 'lrpa': 5,
              'localization': 2, 'loc': 2,
              'cluster': 6,
              'correction': 7, 'correct': 7,
              'results': 8}

    def __init__(self, path=''):
        self.ini_path = path
        self.ini_path = self.set_defalut_ini_path()
        self.cfg = configparser.ConfigParser()
        self.read_ini_file()

        self.project_path, self.start, self.end = self.read_ini_info()
        self.project_name, self.system_type, self.group_type, self.lattice_parameter, self.number_atoms, self.geometry, self.fixed_atoms = self.read_basic_info()
        self.distance_series = self.read_distance_series()
        self.shift_series = self.read_shift_series()
        self.molpro_key, self.molpro_path = self.read_molpro_info()
        self.crystal_path = self.read_crystal_path()
        self.unit = self.get_unit()
        self.ll = self.read_ll()

        if self.start == '' or self.start == 'default':
            self.start = 0
        else:
            self.start = self.start.lower()
            self.start = self.method_dict[self.start]
        if self.end == '' or self.end == 'default':
            self.end = 9
        else:
            self.end = self.end.lower()
            self.end = self.method_dict[self.end]
        jobs = set(range(self.start, self.end))
        jobs.add(3)

        if 0 in jobs:
            self.geo_opt_bs, self.geo_opt_functional, self.geo_opt_nodes = self.read_geo_opt()
        if 1 in jobs:
            self.hf1_bs, self.hf1_nodes = self.read_hf1()
        if 2 in jobs:
            self.loc_nodes = self.read_loc()
        if 3 in jobs:
            self.hf2_bs, self.hf2_nodes = self.read_hf2()
        if 4 in jobs:
            self.lmp2_nodes, self.cryscor_path = self.read_lmp2()
        if 5 in jobs:
            self.rpa_nodes_b, self.rpa_nodes_s, self.memory_b, self.memory_s = self.read_rpa()
        if 6 in jobs:
            self.coord = True
            self.add_h = False
            self.out_layer_number = True
            self.central_atoms, self.factors, self.deleted_atoms = self.read_cluster()
        if 7 in jobs:
            self.correction_nodes, self.correction_memory, self.correction_bs, self.atoms = self.read_correction()

    def set_defalut_ini_path(self):
        if self.ini_path != '':
            return self.ini_path
        else:
            self.ini_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            self.ini_path = os.path.join(self.ini_path, 'input.ini')
            return self.ini_path

    def read_ini_file(self):
        try:
            self.cfg.read(self.ini_path, encoding='utf-8')
        except Exception as e:
            print(e)
        path = self.cfg.get('Initialization', 'path')

    def read_ini_info(self):
        try:
            path = self.cfg.get('Initialization', 'path')
            if path == '':
                path = os.getcwd()
            start = self.cfg.get('Initialization', 'start')
            end = self.cfg.get('Initialization', 'end')
        except configparser.NoOptionError:
            print(configparser.NoOptionError)
            sys.exit()
        return path, start, end

    def read_distance_series(self):
        try:
            distance_series = self.cfg.get('Initialization', 'distance_series')
            distance_series = distance_series.split()
            distance_series = [float(d) for d in distance_series]
            # print(distance_series)
        except configparser.NoOptionError:
            print(configparser.NoOptionError)
            distance_series = 'default'
        return distance_series

    def read_shift_series(self):
        try:
            shift_series = self.cfg.get('Initialization', 'shift_series')
            shift_series = shift_series.split()
            shift_series = [float(d) for d in shift_series]
            # print(shift_series)
        except configparser.NoOptionError:
            print(configparser.NoOptionError)
            shift_series = 'default'
        return shift_series

    def read_ll(self):
        try:
            ll = self.cfg.get('Initialization', 'LL')
            ll = ll.upper()
            ll_list = ['LMP2', 'SCS-LMP2', 'LDRCCD']
            assert ll in ll_list
        except configparser.NoOptionError:
            print(configparser.NoOptionError)
            ll = 'LMP2'
        return ll

    def read_basic_info(self):
        try:
            project_name = self.cfg.get('Basic_Info', 'project_name')
        except configparser.NoOptionError:
            project_name = 'job'
        try:
            system_type = self.cfg.get('Basic_Info', 'system_type')
        except configparser.NoOptionError:
            system_type = 'SLAB'
        try:
            group_type = self.cfg.getint('Basic_Info', 'group_type')
        except configparser.NoOptionError:
            group_type = 1
        try:
            lattice_parameter = self.read_lattice_parameter()
            geometry = self.read_geometry()
            number_atoms = len(geometry)
        except configparser.NoOptionError:
            print(configparser.NoOptionError)
            sys.exit()
        try:
            fixed_atoms = self.read_fixed_atoms()
        except configparser.NoOptionError:
            fixed_atoms = []
        return project_name, system_type, group_type, lattice_parameter, number_atoms, geometry, fixed_atoms

    def read_crystal_path(self):
        try:
            crystal_path = self.cfg.get('Basic_Info', 'crystal_path')
        except configparser.NoOptionError:
            try:
                crystal_path = self.cfg.get('Geo_Opt', 'crystal_path')
            except configparser.NoOptionError:
                print('CRYSTAL path not found.')
                print('Please check input.ini file and try again.')
                sys.exit()
        return crystal_path

    def get_unit(self):
        try:
            unit = self.cfg.get('Initialization', 'unit')
        except configparser.NoOptionError:
            unit = 'hartree'
        return unit

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

    def get_basic_info(self):
        return self.project_name, self.system_type, self.group_type, self.lattice_parameter, self.number_atoms, self.geometry, self.fixed_atoms

    @staticmethod
    def if_none(value):
        if value == '' or value is None:
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

    def get_geometry(self):
        return self.geometry

    @staticmethod
    def if_default(value):
        if value == '' or value is None:
            return 'default'
        else:
            return value

    @staticmethod
    def test_nodes(nodes):
        if is_number(nodes):
            return True
        else:
            if nodes == '':
                return True
            else:
                print('Please enter the right nodes number!')
                return False

    def read_geo_opt(self):
        bs = self.cfg.get('Geo_Opt', 'basis_set')
        bs = self.if_default(bs)
        functional = self.cfg.get('Geo_Opt', 'functional')
        functional = self.if_default(functional)
        if functional == 'default':
            functional = 'PBE0'
        nodes = self.cfg.get('Geo_Opt', 'nodes')
        self.test_nodes(nodes)
        return bs, functional, nodes

    def get_geo_opt(self):
        return self.geo_opt_bs, self.geo_opt_functional, self.geo_opt_nodes, self.crystal_path

    def get_series(self):
        return self.distance_series, self.shift_series

    def read_hf1(self):
        bs = self.cfg.get('HF1', 'basis_set')
        bs = self.if_default(bs)
        nodes = self.cfg.get('HF1', 'nodes')
        self.test_nodes(nodes)
        return bs, nodes

    def get_hf1(self):
        return self.hf1_bs, self.hf1_nodes, self.crystal_path

    def read_hf2(self):
        bs = self.cfg.get('HF2', 'basis_set')
        bs = self.if_default(bs)
        nodes = self.cfg.get('HF2', 'nodes')
        self.test_nodes(nodes)
        return bs, nodes

    def get_hf2(self):
        return self.hf2_bs, self.hf2_nodes, self.crystal_path

    def read_loc(self):
        nodes = self.cfg.get('Localization', 'nodes')
        self.test_nodes(nodes)
        return nodes

    def get_loc(self):
        return self.loc_nodes, self.crystal_path

    def read_lmp2(self):
        nodes = self.cfg.get('LMP2', 'nodes')
        self.test_nodes(nodes)
        cryscor_path = self.cfg.get('LMP2', 'cryscor_path')
        return nodes, cryscor_path

    def get_lmp2(self):
        return self.lmp2_nodes, self.cryscor_path

    def read_rpa(self):
        nodes_rpa_b = self.cfg.get('RPA', 'bilayer_nodes')
        self.test_nodes(nodes_rpa_b)
        nodes_rpa_s = self.cfg.get('RPA', 'singlelayer_nodes')
        self.test_nodes(nodes_rpa_s)
        memory_b = self.cfg.get('RPA', 'bilayer_memory')
        memory_s = self.cfg.get('RPA', 'singlelayer_memory')
        return nodes_rpa_b, nodes_rpa_s, memory_b, memory_s

    def get_rpa(self):
        return self.rpa_nodes_b, self.memory_b, self.rpa_nodes_s, self.memory_s, self.molpro_path, self.molpro_key

    def read_cluster(self):
        central_atoms = self.read_central_atoms_info()
        factors = self.read_factors()
        deleted_atoms = self.read_deleted_atoms()
        self.coord = self.read_coord()
        self.add_h = self.read_if_add_h()
        self.out_layer_number = self.if_out_with_layer_number()
        return central_atoms, factors, deleted_atoms

    def get_cluster(self):
        return self.central_atoms, self.factors, self.deleted_atoms, self.coord, self.add_h, self.out_layer_number

    def read_central_atoms_info(self):
        try:
            upper_center_atoms = self.cfg.get('Cluster', 'upper_center_atoms')
        except configparser.NoOptionError:
            upper_center_atoms = []
        try:
            under_center_atoms = self.cfg.get('Cluster', 'under_center_atoms')
        except configparser.NoOptionError:
            under_center_atoms = []
        upper_center_atoms = self.split_atoms(upper_center_atoms)
        under_center_atoms = self.split_atoms(under_center_atoms)
        central_atoms = self.process_center_atoms(
            upper_center_atoms, under_center_atoms)
        return central_atoms

    @staticmethod
    def split_atoms(atoms):
        if atoms == '' or atoms is None or atoms == []:
            atoms = []
        else:
            atoms = atoms.split()
        return atoms

    @staticmethod
    def process_center_atoms(upper_atoms, under_atoms):
        if upper_atoms != [] and under_atoms != []:
            atoms = [upper_atoms, under_atoms]
        elif upper_atoms == [] and under_atoms != 0:
            atoms = under_atoms
        elif upper_atoms != [] and under_atoms == []:
            atoms = upper_atoms
        else:
            atoms = []
        return atoms

    def read_factors(self):
        try:
            factors_upper = self.cfg.get('Cluster', 'upper_factors')
        except configparser.NoOptionError:
            factors_upper = []
        try:
            factors_under = self.cfg.get('Cluster', 'under_factors')
        except configparser.NoOptionError:
            factors_under = []
        factors_upper = self.split_factors(factors_upper)
        factors_under = self.split_factors(factors_under)
        if len(factors_upper) > 0 and len(factors_under) > 0:
            factors = [factors_upper, factors_under]
        elif len(factors_upper) > 0 and len(factors_under) == 0:
            factors = [factors_upper, factors_upper]
        elif len(factors_upper) == 0 and len(factors_under) > 0:
            factors = [factors_under, factors_under]
        else:
            factors = []
        return factors

    @staticmethod
    def split_factors(factors):
        if factors == '' or factors == []:
            factors = []
        else:
            try:
                factors = factors.split()
                factors = [float(fac) for fac in factors]
            except Exception as e:
                print(e)
        return factors

    def read_coord(self):
        try:
            self.coord = self.cfg.get('Cluster', 'coord')
            assert isinstance(self.coord, str)
            if self.coord.lower() == 'false':
                self.coord = False
            else:
                self.coord = True
        except configparser.NoOptionError:
            self.coord = False
        return self.coord

    def read_deleted_atoms(self):
        try:
            deleted_atoms = self.cfg.get('Cluster', 'deleted_atoms')
            deleted_atoms = self.split_atoms(deleted_atoms)
        except configparser.NoOptionError:
            deleted_atoms = []
        return deleted_atoms

    def read_if_add_h(self):
        try:
            self.add_h = self.cfg.get('Cluster', 'add_h')
            assert isinstance(self.add_h, str)
            if self.add_h.lower() == 'false' or self.add_h == '':
                self.add_h = False
            else:
                self.add_h = True
        except configparser.NoOptionError:
            self.add_h = False
        return self.add_h

    def if_out_with_layer_number(self):
        try:
            self.out_layer_number = self.cfg.get('Cluster', 'output_with_layer_numer')
            assert isinstance(self.out_layer_number, str)
            if self.out_layer_number.lower() == 'false' or self.out_layer_number == '':
                self.out_layer_number = False
            else:
                self.out_layer_number = True
        except configparser.NoOptionError:
            self.out_layer_number = False
        return self.out_layer_number

    def read_molpro_info(self):
        try:
            molpro_key = self.cfg.get('Initialization', 'molpro_KEY')
        except configparser.NoOptionError:
            molpro_key = ''
        try:
            molpro_path = self.cfg.get('Initialization', 'molpro_path')
        except configparser.NoOptionError:
            molpro_path = ''
        return molpro_key, molpro_path

    def read_correction(self):

        try:
            basis_set = self.cfg.get('Correction', 'basis_set')
        except configparser.NoOptionError:
            # print(e)
            basis_set = ''
        try:
            atom1 = self.cfg.get('Correction', 'atom1')
            atom2 = self.cfg.get('Correction', 'atom2')
            atom1 = atom1.split()
            atom2 = atom2.split()
        except configparser.NoOptionError as e:
            print(e)
            atom1, atom2 = [], []

        options = self.cfg.options('Correction')
        nodes = [node for node in options if node.endswith('nodes')]
        nodes_dict = {}
        for node in nodes:
            nodes_dict[node.rsplit('_', 1)[0]] = self.cfg.get('Correction', node)

        memory = [m for m in options if m.endswith('memory')]
        memory_dict = {}
        for m in memory:
            memory_dict[m.rsplit('_', 1)[0]] = self.cfg.get('Correction', m)

        return nodes_dict, memory_dict, basis_set, [atom1, atom2]

    def get_correction(self):
        return self.correction_nodes, self.correction_memory, self.correction_bs, self.molpro_path, self.molpro_key, self.atoms

    def get_cal_parameters(self, step):
        # get necessary options
        options = self.cfg.options(step)
        default_options = ['basis_set', 'functional', 'path', 'nodes', 'memory', 'atom']
        # print(options)
        delete_options = []
        for opt in default_options:
            for o in options:
                if opt in o:
                    # print(o)
                    delete_options.append(o)
        curr_options = list(set(options) - set(delete_options))
        # read the data according to each option
        option_dict = {}
        for opt in curr_options:
            try:
                value = self.cfg.get(step, opt)
                option_dict[opt] = value
            except configparser.NoOptionError as e:
                print(e)
        return option_dict


def exit_programm():
    try:
        import sys
        sys.exit(1)
    except:
        print('INPUT form not correct!!!')
    finally:
        print('''
        Programm Exit...
    --------------------------------------------------------------------------------------------------------------------''')


if __name__ == '__main__':

    def test_read_ini():
        path = os.path.dirname(__file__)
        path = os.path.dirname(path)
        Ini = ReadIni()
        Ini.get_cal_parameters('Geo_Opt')

    test_read_ini()
