import os
from Common import Job_path
from CLUSTER.atom import Atom
import CLUSTER



def test_cut_cluster(job):
    Clu = CLUSTER.Cluster(job, center=[3,4], name='BlackP', size='XS')
    nat = Clu.nat[0]
    x = Clu.x[0]
    y = Clu.y[0]
    z = Clu.z[0]
    atom = CLUSTER.Atom(nat, x, y, z)
    cent = Clu.centre
    test_cal_dis(atom, cent, Clu)
    test_cal_vec_dis(atom, cent, Clu)
    # test_choose_atom(Clu)
    # test_get_layer(Clu)
    # test_cal_atom_dis(Clu)
    # test_cal_coordniate_number(Clu)
    # test_cal_coor_all_atoms(Clu)
    # test_select_atoms_according_coor(Clu)
    Clu.write_xyz()
    # Clu.get_l


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




def test_suite():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\geo_opt'
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'geo_opt.out' in files:
            job = Job_path(root)
            jobs.append(job)
    job = jobs[0]
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster'
    CLUSTER.creat_json_file(path)

    test_cut_cluster(job)



test_suite()
