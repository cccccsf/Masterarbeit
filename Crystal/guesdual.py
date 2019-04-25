#!/usr/bin/python3
from Crystal import Basis_set
from Crystal import Geometry

class Guesdual(object):


    def __init__(self, bs):
        self.title = 'GUESDUAL'
        self.nfr = 0    #number of modification(nfr >= 1)in the atomic basis set given in input
        self.ic = 0     #1:complete SCF calculation 0:stop before the first hamiltonian matrix diagonalization
        self.nat = []   #formal atomic number of the atom whose basis set is modified
        self.nsh = []   #sequence number of the reference shell inthe atomic basis set, starting from which shell(s) is(are) inserted/deleted
        self.nu = []    #number of shells insertedt/deleted after the reference shell NSH
        self.guesdual_info = []
        self.bs = bs

        self.value_init()


    def __len__(self):
        return len(self.nat)

    def __str__(self):
        string = ''
        string += self.guesdual_info[0] + '\n'
        for i in self.guesdual_info[1]:
            string += str(i) + ' '
        string += '\n'
        for shell in self.guesdual_info[2]:
            for unit in shell:
                string += str(unit) + ' '
            string += '\n'
        return string


    def get_guesdual_info(self):
        self.guesdual_info.append(self.title)
        summary_into = []
        summary_into.append(self.nfr)
        summary_into.append(self.ic)
        self.guesdual_info.append(summary_into)

        assert(len(self.nat) == self.nfr)
        assert(len(self.nsh) == self.nfr)
        assert(len(self.nu) == self.nfr)
        shells = []
        for i in range(len(self.nat)):
            shell = []
            shell.append(self.nat[i])
            shell.append(self.nsh[i])
            shell.append(self.nu[i])
            shells.append(shell)
        self.guesdual_info.append(shells)


    def getstring(self):
        return self.string

    def get_nat(self):
        self.nat = self.bs.elements_unique

    def set_ic(self, value):
        assert(value == 0 or value == 1)
        self.ic = value

    def get_nfr(self):
        self.nfr = len(self.nat)

    def get_nsh_and_nu(self):
        for i in range(len(self.nat)):
            self.nu.append(len(self.bs.basis_set[i]))
        self.bs.reset_bs('method', 'HF1')
        for i in range(len(self.nat)):
            self.nsh.append(len(self.bs.basis_set[i]))
            self.nu[i] = self.nu[i] - self.nsh[i]

    def value_init(self):
        self.get_nat()
        self.get_nfr()
        self.get_nsh_and_nu()
        self.get_guesdual_info()

    def write_guesdual(self, path):
        with open(path, 'a') as f:
            f.write(self.guesdual_info[0] + '\n')
            for i in self.guesdual_info[1]:
                f.write(str(i) + ' ')
            f.write('\n')
            for shell in self.guesdual_info[2]:
                for unit in shell:
                    f.write(str(unit) + ' ')
                f.write('\n')
            f.write('END' +'\n')


# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# geo = Geometry(path)
# elements = geo.elements
# method = 'HF2'
# bs = Basis_set(elements, method)
# gd = Guesdual(bs)
# print(gd)



