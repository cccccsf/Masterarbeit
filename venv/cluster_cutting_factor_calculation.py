#!/usr/bin/python3
import os
import CLUSTER
from CLUSTER import Cluster
from CLUSTER import FactorCalculator
from Common import Job_path
from test_cluster import read_infomation


def factor_calculation():

    # parameters input
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\geo_opt\x_1\z_1'
    name = 'SiO2-H2O'
    center = [2, 4]
    atom = (-8.963974190, -5.145932334, -4.090258797)
    atom2 = (0.127722861, 5.352278396, -4.090258797)
    atom3 = (-0.8963974190, -5.145932334, -4.090258797)
    atom4 = (1.599471044, -7.886938139, -4.226003836)
    atom5 = (-7.49226007, 2.6112570791, -4.226003836)
    atom6 = (1.599471044, -7.886938139, -4.226003836)
    atoms = [atom, atom2, atom3, atom4, atom5, atom6]
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

