#!/usr/bin/python3
import os
import re
from Common import read_all_results


def get_layer_distance(path):

    f = open(path + '/hf.out', 'r')
    lines = f.read().replace('\n', ':')
    lines = ' '.join(lines.split()) + '#'
    f.close()

    #search geometry infomation
    regex = ' ATOM AT. N. .*#'
    geo_block = re.search(regex, lines).group(0)
    geo_block = re.split(':', geo_block.replace(': ', ':'))
    geometry = []
    for line in geo_block[1:]:
        if line == '':
            break
        geometry.append(line)

    #get the dict of the z coordinate of each atom
    geometry_split = []
    for geo in geometry:
        geometry_split.append(geo.split())
    z = []
    for geo in geometry_split:
        z.append(geo[-1])

    #get the layer distance by calculating the largest distance between atoms
    distance = 0
    for i in range(1, len(z)):
        if (abs(z[i] - z[i-1])) > distance:
            distance = abs(z[i] - z[i-1])

    return distance


def read_init_distance(path):
    path = os.path.split()[0]
    path = os.path.split()[0]
    path = os.path.split(path)[0]
    path = path + '/geo_opt'
    with open(path, 'r') as f:
        init_dist = f.read()
    init_dist = init_dist.strip()
    init_dist = float(init_dist)
    return init_dist


def get_energy(job):
    path = job.path
    f = open(path + '/hf.out', 'r')
    lines = f.read()
    lines = ' '.join(lines.split()) + '#'
    f.close()

    #regex = 'SCF ENDED - CONVERGENCE ON ENERGY .* CYCLES'
    regex = 'SCF ENDED .* CYCLES'
    try:
        energy_block = re.search(regex, lines).group(0)    #SCF ENDED - CONVERGENCE ON ENERGY E(AU) -2.7260361085525E+03 CYCLES
        status = if_converged(energy_block)
        if status == True:
            regex_2 = 'E\(AU\) .* '
            energy_block = re.search(regex_2, energy_block).group(0)    #E(AU) -2.7260361085525E+03
            regex_3 = ' .* '
            energy_block = re.search(regex_3, energy_block).group(0)    # -2.7260361085525E+03
            energy = energy_block[1:-1]    #str
            job.set_status('finished')
        else:
            energy = 'Nah'
            print('---'*15)
            print(job)
            print('Calculation not converged.')
            print('Please check the output file and change some parameters to recalculate the job.')
            job.set_status('not converged')
    except AttributeError as e:
        print('---'*15)
        print(job)
        print('Energy not found.')
        print('Please check the output file.')
        energy = 'Nah'
        job.set_status('error')

    return energy


def if_converged(energy_block):
    regex = '- .*?E\('
    try:
        status = re.search(regex, energy_block).group(0)
        status = status[2:-3]
        if status == 'CONVERGENCE ON ENERGY':
            return True
        elif status == 'TOO MANY CYCLES':
            return False
        else:
            print('---'*15)
            print(path)
            print('Status not found.')
            print('Please check the output file.')
            return False
    except AttributeError as e:
        print('---'*15)
        print(path)
        print('Status not found.')
        print('Please check the output file.')



def get_all_x_and_z(paths, init_distance):
    x_set = set()
    z_set = set()
    for path in paths:
        z = os.path.split(path)[-1]
        path = os.path.split(path)[0]
        layer_type = 'bilayer'
        if z == 'underlayer' or z =='upperlayer':
            layer_type = z
            z = os.path.split(path)[-1]
            path  = os.path.split(path)[0]
        z = float(z.split('_')[-1])
        x = os.path.split(path)[-1]
        x = float(x.split('_')[-1])
        x_set.add(x)
        z_set.add(z)
    x_list = list(xs)
    z_list = list(zs)
    x_list.sort()
    z_list.sort()
    for i in range(len(z_list)):
        z_list[i] = z_list[i] +  init_distance
    x_dict = {}
    z_dict = {}
    for i in range(len(x_list)):
        x_dict[x_list[i]] = i
    for i in range(len(z_list)):
        z_dict[z_list[i]] = i
    return x_dict, z_dict


def get_x_z_and_layertype(path, init_distance):
    z = os.path.split(path)[-1]
    path = os.path.split(path)[0]
    layer_type = 'bilayer'
    if z == 'underlayer' or z =='upperlayer':
        layer_type = z
        z = os.path.split(path)[-1]
        path  = os.path.split(path)[0]
    z = float(z.split('_')[-1])
    z = z + init_distance
    x = os.path.split(path)[-1]
    x = float(x.split('_')[-1])
    return x, z, layer_type


def creatxls_dis(path):
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('hf1')   #creat new sheet
    ws.write(0, 0, 'displacement')
    ws.write(0, 1, 'distance(A)')
    ws.write(0, 2, 'E(au)')
    ws.write(0, 3, 'Eupperlayer(au)')
    ws.write(0, 4, 'Eunderlayer(au)')
    ws.write(0, 5, 'deltaE')
    wb.save(path + '/hf1.xls')  #save the sheet


def data_saving_dis(i, path, disp, dis, l, energy):
    try:
        file = path + '/hf1.xls'
        rb = xlrd.open_workbook(file, formatting_info=True)
        wb = copy(rb)
        ws = wb.get_sheet(0)
        ws.write(i, 0, str(disp))
        ws.write(i, 1, str(dis))
        ws.write(i, l, str(energy))
        wb.save(path + '/hf1.xls')
    except Exception as e:
        print(e)


def read_and_record_result(path, init_distance):
    energy = get_energy(path)
    x, z, layer_type = get_x_z_and_layertype(path, init_distance)
    #path = path + '/../..'
    path = os.path.dirname(path)
    path = os.path.dirname(path)
    j = 1 + len(x_dict) * z_dict[z] + x_dict[x]
    layer = {'bilayer': 2, 'upperlayer': 3, 'underlayer': 4}
    l = layer[layer_type]
    data_saving_dis(j, path, x, z, l, energy)


def read_all_results_hf1(jobs, init_dist = 3.1):
    read_all_results(jobs, 'hf1', energy_func=get_energy, init_distance=init_dist)
