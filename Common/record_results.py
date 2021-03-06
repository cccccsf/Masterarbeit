#!/usr/bin/python3
import os
import csv
import json
from collections import namedtuple
from Common import rename_file
import Common


def get_init_distance(job):
    path = job.root_path
    path = os.path.join(path, 'geo_opt')
    path = os.path.join(path, 'init_distance')
    with open(path, 'r') as f:
        init_dist = f.read()
    init_dist = init_dist.strip()
    init_dist = float(init_dist)
    return init_dist


def creatcsv(path, cal_type):
    csv_path = os.path.join(path, '{}.csv'.format(cal_type))
    headers = [
        'displacement',
        'distance(A)',
        'E',
        'Eupperlayer',
        'Eunderlayer',
        'Einterlayer']
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(headers)


def creat_json_file(json_file):
    if not os.path.exists(json_file):
        data = {}
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)


def data_saving(path, line, cal_type):
    try:
        csv_path = os.path.join(path, '{}.csv'.format(cal_type))
        with open(csv_path, 'a', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(line)
    except Exception as e:
        print(e)


def read_result(job, energy_func, init_distance):
    path = job.path
    x = job.x
    z = job.get_z_value()
    z = z + init_distance
    z = round(z, 2)
    z = str(z)
    x_z = namedtuple('x_z', ['x', 'z'])
    x_and_z = x_z(x, z)
    if job.method != 'lpm2':
        energy = energy_func(job)
        return x_and_z, energy
    else:
        # should correct then
        Elmp2, Escs_lmp2 = energy_func(path)
        return x_and_z, Elmp2, Escs_lmp2


def read_all_results(jobs, cal_type, energy_func, init_distance=None):

    # get the initial distance of the system
    if init_distance is None:
        try:
            init_distance = get_init_distance(jobs[0])
        except Exception as e:
            print(e)
            init_distance = None
        if init_distance is None:
            while True:
                try:
                    print('Please enter the initial layer distance of the system:')
                    init_distance = input()
                    init_distance = float(init_distance)
                    break
                except Exception as e:
                    print(e)
                    print(
                        'Please enter the right number of the initial layer distance!!!')
                    continue

    path = jobs[0].root_path
    if cal_type != 'scs_lmp2':
        json_file = os.path.join(path, cal_type)
    else:
        json_file = os.path.join(path, 'lmp2')
    json_file = os.path.join(json_file, '{}.json'.format(cal_type))
    creat_json_file(json_file)

    bilayer = {}
    upperlayer = {}
    underlayer = {}
    for i in range(len(jobs)):
        x_and_z, energy = read_result(jobs[i], energy_func, init_distance)
        layertype = jobs[i].layertype
        if layertype == 'bilayer':
            bilayer[x_and_z] = energy
        elif layertype == 'underlayer':
            underlayer[x_and_z] = energy
        elif layertype == 'upperlayer':
            upperlayer[x_and_z] = energy
        # record to json file
        record_to_json(jobs[i], json_file, energy, layertype, init_distance)

    # calculation of layer energy
    layer_energy_dict = {}
    if len(bilayer) > 0 and len(underlayer) > 0:
        for job in jobs:
            if job.layertype == 'bilayer':
                x_and_z, _ = read_result(job, energy_func, init_distance)
                if x_and_z in bilayer and x_and_z in underlayer and x_and_z in upperlayer:
                    layer_energy = Common.cal_layer_energy(bilayer[x_and_z], upperlayer[x_and_z], underlayer[x_and_z])
                    layer_energy_dict[x_and_z] = layer_energy
                    record_to_json(job, json_file, layer_energy, 'layer_energy', init_distance)

    # record to .csv file
    lines = []
    for x_and_z, energy in bilayer.items():
        line = []
        line.append(x_and_z.x)
        line.append(x_and_z.z)
        line.append(energy[0])
        if x_and_z in upperlayer:
            line.append(upperlayer[x_and_z][0])
        else:
            line.append('NaN')
        if x_and_z in underlayer:
            line.append(underlayer[x_and_z][0])
        else:
            line.append('NaN')
        if x_and_z in layer_energy_dict:
            line.append(layer_energy_dict[x_and_z][0])
        else:
            line.append('NaN')
        lines.append(line)

    csv_path = os.path.join(path, '{}.csv'.format(cal_type))
    rename_file(path, '{}.csv'.format(cal_type))
    creatcsv(path, cal_type)
    with open(csv_path, 'a', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(lines)


def record_to_json(job, json_file, energy, layertype='bilayer', init_distance=3.1):
    coord = '{}'.format(job.coord)
    x = job.x
    if is_number(x):
        x = float(x)
    z = job.z
    if is_number(z):
        z = float(z) + init_distance
    with open(json_file, 'r') as f:
        data = json.load(f)
    if coord not in data:
        data[coord] = {}
    path = job.path
    data[coord][layertype] = {
        'energy': energy,
        'x': x,
        'z': z,
        'path': path
    }
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
