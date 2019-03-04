#!/usr/bin/python3
import os
import CLUSTER
from CLUSTER import Cluster
from CLUSTER import FactorCalculator
from Common import Job_path
from test_cluster import read_infomation


def factor_calculation():

    # parameters input
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\geo_opt\x_1\z_2'
    name = 'MgO'
    center_upp = [25, 25]
    center_und = [9, 9]
    center = [center_upp, center_und]
    atom = (-2.99725, 0, 16.835625996)
    atom2 = (-1.498625, 5.352278396, 16.891833116)
    atom3 = (-2.99725, -2.99725, 19.963182233)
    atoms = [atom, atom2, atom3]
    #if needed
    dimen = 2
    lattice_parameter = []
    geometry = []
    vector = []
    dimen, lattice_parameter, geometry = read_infomation(path)


    #calculation part
    job = Job_path(path)
    json_path = os.path.join(job.root_path, 'cluster')
    if not os.path.exists(os.path.join(json_path, 'geometry.json')):
        CLUSTER.creat_json_file(json_path)
    if lattice_parameter != [] and geometry != []:
        basic_info = [dimen, lattice_parameter, geometry]
        Clu = Cluster(job, name=name, centre=center, basic_infos=basic_info)
    else:
        Clu = Cluster(job, name=name, centre=center)
    Fac = FactorCalculator(Clu)

    for atom in atoms:
        dis_fac = Fac.get_distance_to_center(atom, factor=True)
        print('---'*20)
        print(atom)
        print('cluster factor of distance: ', dis_fac)

        if vector == []:
            print(Clu.centre)
            a_fac = Fac.get_distance_to_vector(atom, vec=1, factor=True)
            print('cluster factor of lattice vector 1: ', a_fac)
            b_fac = Fac.get_distance_to_vector(atom, vec=2, factor=True)
            print('cluster factor of lattice vector 2: ', b_fac)
            if Clu.dimensionality != 2:
                c_fac = Fac.get_distance_to_vector(atom, vec=3, factor=True)
                print('cluster factor of lattice vector 3: ', c_fac)
        else:
            fac = Fac.get_distance_to_vector(atom, vector, True)

if  __name__ == "__main__":
    factor_calculation()

