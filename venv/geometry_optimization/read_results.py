#!/usr/bin/python3
import os
import re
import xlwt
import xlrd
import time
from xlutils.copy import copy
from geometry_optimization import submit_job

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
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('geo_opt')   #新建工作表
    ws.write(0, 0, 'displacement')
    ws.write(0, 1, 'distance(A)')
    ws.write(0, 2, 'E(au)')
    wb.save(path + '/geo_opt.xls')  #保存工作表

def data_saving_dis(i, path, disp, dis, energy):
    try:
        file = path + '/geo_opt.xls'
        rb = xlrd.open_workbook(file, formatting_info=True)
        wb = copy(rb)
        ws = wb.get_sheet(0)
        ws.write(i, 0, str(disp))
        ws.write(i, 1, str(dis))
        ws.write(i, 2, str(energy))
        wb.save(path + '/geo_opt.xls')
        count = i
        #print('已写入%d条数据'%count)
    except Exception as e:
        print(e)

def read_and_record_result(j, path, init_distance):
    lattice_parameter, geometry = get_optimized_geometry(path)
    energy = get_optimized_energy(path)
    write_optimized_geometry(path, geometry)
    write_optimized_lattice_parameter(path, lattice_parameter)
    z = os.path.split(path)[-1]
    distance = re.search('_.*', z).group(0)
    distance = distance[1:]
    distance = float(distance) + float(init_distance)
    x = os.path.split(path)[0]
    x = os.path.split(x)[-1]
    displacement = re.search('_.*', x).group(0)
    displacement = displacement[1:]
    path = path + '/../..'
    data_saving_dis(j, path, displacement, distance, energy)

# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# read_and_record_result(path)

def read_all_results(job_dirs, init_distance):
    finished_path = []
    readed_path = []
    creatxls_dis(job_dirs[0] + '/../..')

    def test_finished(paths):
        """
        test one job is finished or not,
        if finished, add the path to list finished_path, and delete it from the original list
        :param paths:
        :return:
        """
        for path in paths:
            if submit_job.if_cal_finish(path):
                finished_path.append(path)
                paths.remove(path)
            else:
                pass
    i = 0
    length = len(job_dirs)
    while i < length:
        test_finished(job_dirs)
        if len(finished_path) > i:
            j = i + 1
            read_and_record_result(j, finished_path[i], init_distance)
            readed_path.append(finished_path[i])
            i += 1
        else:
            time.sleep(500)
            continue


def write_init_distance(path, dist):
    path = path + '/geo_opt'
    with open(path + '/init_distance', 'w') as f:
        f.write(str(dist) + '\n')


# path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
# read_and_record_result(path)

# job_dirs=['C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106', 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_0\\z_0']
# read_all_results(job_dirs, init_distance=3.1)
