#!/usr/bin/python3
import os
import re
import time
import csv
from Common import Job_path


def get_optimized_geometry(path):

    f = open(path + '/geo_opt.out', 'r')
    lines = f.read().replace('\n', ':')
    lines = ' '.join(lines.split()) + '#'
    f.close()

    #search geometry infomation
    regex = 'FINAL OPTIMIZED GEOMETRY.*GEOMETRY OUTPUT FILE'
    geo_block = re.search(regex, lines).group(0)
    regex_2 = 'LATTICE PARAMETERS.*'
    lattice_block = re.search(regex_2, geo_block).group(0)
    lattice_block = re.split(':', lattice_block.replace(': ', ':'))
    """
['LATTICE PARAMETERS (ANGSTROMS AND DEGREES) - BOHR = 0.5291772083 ANGSTROM',
 'PRIMITIVE CELL',
 'A B C ALPHA BETA GAMMA ',
 '3.29400428 4.46278516 500.00000000 90.000000 90.000000 90.001902',
 '*******************************************************************************',
 'ATOMS IN THE ASYMMETRIC UNIT 8 - ATOMS IN THE UNIT CELL',
 '8',
 'ATOM X/A Y/B Z(ANGSTROM)',
 '*******************************************************************************',
 '1 T 15 P -2.500019207010E-01 -4.209460829187E-01 3.632461643661E+00',
 '2 T 15 P 2.500101901927E-01 -9.421278815670E-02 3.641530001473E+00',
 '3 T 15 P 2.500000000000E-01 7.863000000000E-02 1.550000000000E+00',
 '4 T 15 P -2.499815187864E-01 4.061106153149E-01 1.538708898854E+00',
 '5 T 15 P 2.500000000000E-01 -4.213700000000E-01 -1.550000000000E+00',
 '6 T 15 P -2.499864188737E-01 -9.387379184557E-02 -1.539124057504E+00',
 '7 T 15 P -2.499980772885E-01 7.907174242089E-02 -3.632901395412E+00',
 '8 T 15 P 2.500185232964E-01 4.058118423740E-01 -3.641552477004E+00',
 '',
 'T = ATOM BELONGING TO THE ASYMMETRIC UNIT',
 'INFORMATION **** fort.34 **** GEOMETRY OUTPUT FILE']
 """
    i = 0
    sep = []
    for l in lattice_block:
        if l == '*******************************************************************************':
            sep.append(i)
        i +=1

    lattice_parameter = lattice_block[sep[0]-1]
    lattice_parameter = lattice_parameter.split()

    geometry = []
    j = 1
    for l in lattice_block[9:]:
        if len(l) > 3 and l[0] == str(j):
            geometry.append(l)
            j += 1
    geometry_split = []
    for geo in geometry:
        geometry_split.append(geo.split())
    for geo in geometry_split:
        del geo[0]
        del geo[0]
        del geo[1]

    return lattice_parameter, geometry_split


def get_optimized_energy(path):
    f = open(path + '/geo_opt.out', 'r')
    lines = f.read()
    lines = ' '.join(lines.split()) + '#'
    f.close()

    regex = 'OPT END.* POINTS'
    energy_block = re.search(regex, lines).group(0)
    regex_2 = ': .* '
    energy_block = re.search(regex_2, energy_block).group(0)
    energy = energy_block[2:-1]

    return energy


def write_optimized_geometry(path, geometry):
    with open(path + '/optimized_geometry', 'w') as f:
            for geo in geometry:
                for unit in geo:
                    f.write(unit + ' ')
                f.write('\n')


def write_optimized_lattice_parameter(path, lattice):
    with open(path + '/optimized_lattice_parameter', 'w') as f:
            for unit in lattice:
                f.write(unit + ' ')


def creatxls_dis(path):
    csv_path = os.path.join(path, 'geo_opt.csv')
    headers = ['displacement', 'distance(A)', 'E(au)']
    with open(csv_path, 'w', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)


def data_saving(i, path, disp, dis, energy):
    try:
        csv_path = os.path.join(path, 'geo_opt.csv')
        new_line = [str(disp), str(dis), str(energy)]
        with open(csv_path, 'a', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(new_line)
        count = i
        print('%d data has been written '%count)
    except Exception as e:
        print(e)


def read_and_record_result(j, job, init_distance):
    path = job.path
    lattice_parameter, geometry = get_optimized_geometry(path)
    energy = get_optimized_energy(path)
    write_optimized_geometry(path, geometry)
    write_optimized_lattice_parameter(path, lattice_parameter)
    distance = job.z
    distance = float(distance) + float(init_distance)
    displacement = job.x
    path = job.root_path
    data_saving(j, path, displacement, distance, energy)


def read_all_results(jobs, init_distance):
    readed_path = []
    creatxls_dis(jobs[0].root_path)

    j = 1
    for i in range(len(jobs)):
        read_and_record_result(j, jobs[i], init_distance)
        readed_path.append(jobs[i])
        j += 1





def test_data_saving():
    path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\geo_opt\\x_-0.150\\z_-0.106'
    energy = get_optimized_energy(path)
    job = Job_path(path)
    path = job.root_path
    creatxls_dis(path)
    read_and_record_result(2, job, 3.1)


def test_read_all_results():
    path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test'
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'geo_opt.out' in files:
            job = Job_path(root)
            jobs.append(job)
    read_all_results(jobs, 3.1)


def test_suite():
    #test_data_saving()
    test_read_all_results()

#test_suite()

