#!/usr/bin/python3
from Data import Periodict_Table
from Basis_Set import basis_set_catalog
from Data import Functionals

yes_or_no = {'Y':1, 'y':1, 'Yes':1, 'yes':1, 'N':0, 'n':0, 'No':0, 'no':0 }


class Geo_Init:

    def __init__(self):
        self.name = ''
        self.slab_or_molecule = ''
        self.layer_group = 1
        self.lattice_parameter = []
        self.number_of_atoms = 0
        self.geometry_info = []

    def add_basic_info(self):
        print('Which system do you want to caculate?')
        self.name = input('Please enter the name of the system:')
        print('You want to calculate this system:' + '\n' + self.name)
        print('Which type is your system? Slab or Molecule?')
        self.slab_or_molecule = str.upper(input('Please enter your type:'))
        while self.slab_or_molecule != 'SLAB' and self.slab_or_molecule != 'MOLECULE':
            print('Please enter the right type')
            self.slab_or_molecule = str.upper(input('Please enter your type:'))
        print('Please enter the number of layer groups(Slab) or point groups(Molecule) for your system according to the Appendix')

        while True:
            layer_group = input()
            try:
                self.layer_group = int(self.layer_group)
                if self.slab_or_molecule == 'SLAB':
                    while self.layer_group < 1 or self.layer_group > 80:
                        print('Please enter the right number')
                        self.layer_group = int(input())
                    break
                else:
                    while self.layer_group < 1 or self.layer_group > 47:
                        print('Please enter the right number')
                        self.layer_group = int(input())
                    break
            except ValueError as e:
                print(e, 'Please enter the right number')
                continue

    def add_lattice_parameter(self):
        print('Please enter the lattice parameter:')
        para = input()
        self.lattice_parameter.append(para)
        while True:
            print('''
Do you want to continually enter the lattice parameter?
Please enter the lattice parameter below,
Or enter the key ENTER to finish.
            ''')
            finish = '' \
                     ''
            parameter = input()
            if parameter == finish:
                break
            else:
                self.lattice_parameter.append(parameter)

    def split_geo_info(self, string):
        coordination = string.split(', ')
        if len(coordination) == 1:
            coordination = string.split(',')
        return coordination

    def add_geo_info(self):
        print('Please enter the number of atoms of your system:')
        self.number_of_atoms = input()
        count = int(self.number_of_atoms) - 1
        print('''
Please enter the coordinate of the atom according to following:
###############################################################################################################
###                                                                                                         ###
###    15, -2.500000000000E-01, -4.213700000000E-01, 3.700000000000E+00   #   Z = 15, Phosphorus; x, y, z   ###
###    --------------------------------------------------------------------------------------------------   ###
###                                                                                                         ###
###    For slab, x, y are in fraction and z is in Ångström                                                  ###                
###    For melecule, x, y and z are all in Ångström                                                         ###
###                                                                                                         ###    
###############################################################################################################
''')
        coord_0 = input()
        coords_0 = self.split_geo_info(coord_0)
        self.geometry_info.append(coords_0)
        while count > 0:
            print('''
Please enter the atom infomation below,
Or enter the key ENTER to finish.
            ''')
            finish = '' \
                     ''
            coord_1 = input()
            if coord_1 == finish:
                break
            else:
                coords_1 = self.split_geo_info(coord_1)
                self.geometry_info.append(coords_1)
            count -= 1

    def initialization(self):
        self.add_basic_info()
        print('Do you want to enter the lattice parameter?(Y/n)')
        if_lattice_parameter = 1
        if_la_pa = input()
        if_lattice_parameter = yes_or_no[if_la_pa]
        if if_lattice_parameter == 1:
            self.add_lattice_parameter()
        print('Do you want to enter the gemetry infomation?(Y/n)')
        if_geometry_infomation = 1
        if_geo_info = input()
        if_geometry_infomation = yes_or_no[if_geo_info]
        if if_geometry_infomation == 1:
            self.add_geo_info()

        return self.name, self.slab_or_molecule, self.layer_group, self.lattice_parameter, self.number_of_atoms, self.geometry_info

#aaa = Initialization()
#aaa.initialization()

class Bs_Init():

    def __init__(self, geometry_info, bs_type=''):
        self.geometry_info = geometry_info
        self.elements = []
        self.if_metals = []
        self.bs_types = [bs_type]
        self.bs_type = bs_type
        self.num_bs_types = {}

    def gen_element(self):
        #print(self.geometry_info)
        for atom in self.geometry_info:
            if type(atom) == str:
                #print(atom)
                atom = atom.split()
            #print(atom)
            self.elements.append(atom[0])
        elements = set(self.elements)
        elements = list(elements)
        elements.sort()
        self.elements = elements
        return elements    #z. B. [6, 16, 15, 26]  ##['C', 'S', 'P', 'Fe']

    def if_metal(self, elements):
        metal = 0
        for ele in elements:
            if ele in Periodict_Table.metal_rev:
                metal = 1
                self.if_metals.append(metal)
            else:
                metal = 0
                self.if_metals.append(metal)
        #z. B. if_metals = [0, 0, 0, 1]

    def bs_type_default(self):
        count = 0
        type = 'POB-TZVP'
        for i in self.if_metals:
            if i == 1:
                type = 'POB-TZVP'
                self.bs_types.append(type)
            elif i == 0:
                type ='AHLRICHS'
                self.bs_types.append(type)
        #print(self.bs_types)
        #z. B. bs_types = ['AHLRICHS', 'AHLRICHS', 'AHLRICHS', 'POB-TZVP']

    #generation of the dict of the atomic number to basis set type
    def gen_num_bs(self):
        i = 0
        for ele in self.elements:
            self.num_bs_types[ele] = self.bs_types[i]
            i += 1
        #z. B. num_bs_types = {6: 'AHLRICHS', 16: 'AHLRICHS', 15: 'AHLRICHS', 26: 'POB-TZVP'}

    def if_bs_change(self):
        print('Do you want to change the Basis Set type?')
        if_bs = input()
        if_bs_change = yes_or_no[if_bs]
        return if_bs_change

    def enter_bs(self):
        while True:
            print('Please enter which type of Basis Set you want to choose:')
            bs_type = input()
            bs_type = bs_type.lower()
            if bs_type not in basis_set_catalog.bs_namen_lower:
                print('''
                Please enter appropriate basis set type!!!
                You can cheak the appendix to see which types we support
                ''')
            else:
                break
        return bs_type

    def gen_bs_info(self, if_bs_change):
        if if_bs_change == 1:
            if len(self.bs_type) == 0:
                bs_type =self.enter_bs()
            elements = self.gen_element()
            #print(elements)
            self.if_metal(elements)
            for i in range(len(self.if_metals)):
                self.bs_types.append(self.bs_type)
        else:
            elements = self.gen_element()
            self.if_metal(elements)
            self.bs_types = []
            self.bs_type_default()
        self.gen_num_bs()

        ele_to_bs_type = self.num_bs_types
        return ele_to_bs_type, elements

    def initialization(self):
        if_bs_change = self.if_bs_change()
        ele_to_bs_type, elements = self.gen_bs_info(if_bs_change)
        return if_bs_change, ele_to_bs_type, elements


class Cal_Init():

    def __init__(self):
        #self.ele_to_bs_type = ele_to_bs_type
        #self.method_type = 'PBE0'
        pass

    def functional_init(self):
        print('Do you want to choose other functional?')
        if_bs_change = 0
        if_bs = input()
        if_bs_change = yes_or_no[if_bs]
        if if_bs_change == 1:
            while True:
                print('Which functional do you want to choose?')
                functional= input()
                functional = functional.upper()
                if functional not in Functionals.correlat or Functionals.exchange or Functionals.functionals:
                    print('''
                        Please enter appropriate functional name!!!
                        You can cheak the appendix to see which types we support
                        ''')
                else:
                    break
        else:
            functional = 'PBE0'
        return functional








