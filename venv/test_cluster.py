import os
from Common import Job_path
from CLUSTER.atom import Atom
import CLUSTER
from CLUSTER.atom import Atom


#test BlackP

def test_cut_cluster(job):
    fac_upp = [1.2, 1.8, 1.3]
    fac_und = [1.2, 1.8, 1.3]
    factors = [fac_upp, fac_und]
    Clu = CLUSTER.Cluster(job, centre=[[3, 4], [7, 8]], name='BlackP', factors=factors,size='L')
    nat = Clu.nat[0]
    x = Clu.x[0]
    y = Clu.y[0]
    z = Clu.z[0]
    atom = CLUSTER.Atom(nat, x, y, z)
    cent = Clu.centre
    test_cal_dis(atom, cent, Clu)

    #test_cal_vec_dis(atom, cent, Clu)
    # test_choose_atom(Clu)
    # test_get_layer(Clu)
    # test_cal_atom_dis(Clu)
    # test_cal_coordniate_number(Clu)
    # test_cal_coor_all_atoms(Clu)
    # test_select_atoms_according_coor(Clu)
    Clu.write_xyz_with_layernumber()
    # Clu.get_l
    # Clu.add_H()


def test_cal_dis(atom, cent, Clu):
    dis = Clu.cal_distance(atom, cent)
    #print(dis)

def test_cal_vec_dis(atom, cent, Clu):
    vec =Clu.lattice_vector[0]
    dis = Clu.cal_vec_distance(atom, cent, vec)



def test_choose_atom(Clu):
    Clu.choose_atoms_from_distance()


def test_get_layer(Clu):
    Clu.get_layer_distance()
    Clu.get_layers()


def test_cal_atom_dis(Clu):
    atom1 = Clu.geometry[2]
    atom1 = Atom(atom1[1], atom1[3], atom1[4], atom1[5])
    atom2 = Clu.geometry[3]
    atom2 = Atom(atom2[1], atom2[3], atom2[4], atom2[5])
    dis = Clu.cal_dis_two_atoms(atom1, atom2)
    expected = 2.2207291971357184
    assert dis == expected


def test_cal_coordniate_number(Clu):
    dict0 = Clu.cal_coordinate_number_of_original_atoms()
    expected = {'1': 3, '2': 3, '3': 3, '4': 3, '5': 3, '6': 3, '7': 3, '8': 3}
    assert dict0 == expected

def test_select_atoms_according_coor(Clu):
    atoms = Clu.select_atoms_according_coordinate(Clu.choosed_atoms)


def test_cal_coor_all_atoms(Clu):
    Clu.cal_coor_no_of_all_atoms(Clu.choosed_atoms)




def test_blackP():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\geo_opt'
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'geo_opt.out' in files:
            job = Job_path(root)
            jobs.append(job)
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster'
    #path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\cluster'
    CLUSTER.creat_json_file(path)
    # job = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\geo_opt\x_1\z_1'
    job = jobs[0]
    # print(job)
    # # job = Job_path(job)
    test_cut_cluster(job)
    # for job in jobs:
    #     test_cut_cluster(job)



def read_infomation(path):
    file = os.path.join(path, 'inp')
    with open(file) as f:
        lines = f.readlines()
    lattice = lines[:3]
    lattice = [line.strip().split() for line in lattice]
    lattice = [(float(l[0]), float(l[1]), float(l[2])) for l in lattice]
    geo = lines[4:]
    geo = [g.strip().split() for g in geo]
    for g in geo[:]:
        g[-1] = float(g[-1])
        g[-2] = float(g[-2])
        g[-3] = float(g[-3])
    dimen = 2
    return dimen, lattice, geo


#test SiO-H2O

def test_SiO2():

    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\cluster'
    #path = r'/users/shch/project/Masterarbeit/Test/cluster'
    CLUSTER.creat_json_file(path)
    job = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\geo_opt\x_1\z_1'
    #job = r'/users/shch/project/Masterarbeit/Test/geo_opt/x_1/z_1'
    dimen, lattice, geo = read_infomation(job)
    job = Job_path(job)
    #centre=[16, 16]
    centre = [2, 4]
    fac_upp = [0.85, 1.1, 1.1]
    fac_und = fac_upp
    factors = [fac_upp, fac_und]
    deleted_atoms = [54, 49]
    #deleted_atoms = []
    #centre = [[2, 2], [13, 13]]
    Clu = CLUSTER.Cluster(job, name='SiO2-H2O', centre=centre, basic_infos=[dimen, lattice, geo], factors=factors, size='M', fixed_atoms=[10, 17], deleted_atoms=deleted_atoms)
    original_atoms = Clu.original_atoms
    cnt = 1
    Clu.write_xyz()
    # for atom in original_atoms:
        # print(cnt, atom)
        # cnt += 1
        #print(atom.no, atom.z, atom.nat, atom.coor, atom.coor_vec)
    # for atom in Clu.choosed_atoms:
    #     print(cnt, atom.no, atom.nat, atom.coor, atom.coor_vec_free)
    #     cnt += 1
    #Clu.write_xyz()
    # print(Clu.dimensionality)
    # print(original_atoms[0])
    # print(original_atoms[0].coor_vec)

    #test_FactorCalculator(Clu)

def test_FactorCalculator(Cluster):
    CLUSTER.FactorCalculator(Cluster)

# test MgO

def test_MgO():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\cluster'
    CLUSTER.creat_json_file(path)
    job = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\geo_opt\x_1\z_2'
    dimen, lattice, geo = read_infomation(job)
    job = Job_path(job)
    center_upp = [25, 25]
    center_und = [9, 9]
    center = [center_upp, center_und]
    fixed_atoms = [13, 24]
    fac_upp = [0.3, 0.5, 0.5]
    fac_und = [0.4, 0.6, 0.6]
    factors = [fac_upp, fac_und]
    Clu = CLUSTER.Cluster(job, name='MgO', centre=center, basic_infos=[dimen, lattice, geo], factors=factors, fixed_atoms=fixed_atoms)
    Clu.final_cluster = Clu.choose_atoms_from_distance()
    Clu.write_xyz(Clu.choosed_atoms)
    # original_atoms = Clu.original_atoms
    # cnt = 1
    # Clu.write_xyz()





def test_suite():
    #test_blackP()
    #test_SiO2()
    test_MgO()
    pass

test_suite()

