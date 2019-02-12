#!/usr/bin/python3
import os
import re
import json


def read_block(job):

    path = job.path
    out_file = os.path.join(path, 'geo_opt.out')
    with open(out_file, 'rb') as f:
        f.seek(-20000, 2)
        out = f.read().decode('utf-8')

    #search final optimized geometry
    reg = 'FINAL OPTIMIZED GEOMETRY.*'
    block = re.search(reg, out, re.M|re.S)
    if block != None:
        block = block.group(0)
    else:
        print(path)
        print('Iinfomation not found...')
        return None
    return  block


def get_dimensionality(block):

    reg = 'FINAL OPTIMIZED GEOMETRY.*?\n'
    dimen = re.search(reg, block, re.M|re.S)
    if dimen != None:
        dimen = dimen.group(0)
    else:
        print('Dimensionality not found...')
        return None

    dimen = dimen.strip()
    dimensionality = dimen[-1]
    try:
        dimensionality = float(dimensionality)
        return dimensionality
    except Exception as e:
        print(e)
        print('Tring again using RE.')
        try:
            reg = '[1-9]'
            dimen = re.search(reg, dimen).group(0)
            dimensionality = float(dimen)
            return dimensionality
        except Exception as e:
            print(e)
            print('Can not found Dimensionality...')


def get_lattice_vector(block):

    reg = 'DIRECT LATTICE VECTORS CARTESIAN COMPONENTS.*?\n.*?\n.*?\n.*?\n.*?\n'
    latt_vec = re.search(reg, block, re.M|re.S)
    if latt_vec != None:
        latt_vec = latt_vec.group(0)
    else:
        print('Dimensionality not found...')
        return None
    latt_vec = latt_vec.strip('\n')
    latt_vec = latt_vec.split('\n')
    latt_vec = latt_vec[-3:]
    try:
        for i in range(len(latt_vec)):
            latt_vec[i] = latt_vec[i].strip()
            latt_vec[i] = latt_vec[i].split()
            for j in range(len(latt_vec[i])):
                latt_vec[i][j] = float(latt_vec[i][j])
    except Exception as e:
        print(e)
        print('Can not found lattice vector...')
        return None
    return latt_vec


def get_geometry(block):

    reg = 'CARTESIAN COORDINATES.*?TRANSLATORS IN FRACTIONAL UNITS'
    geo = re.search(reg, block, re.M|re.S)
    if geo != None:
        geo = geo.group(0)
    else:
        print('Dimensionality not found...')
        return None
    reg = '    1.*\n\n'
    geometry = re.search(reg, geo, re.M|re.S)
    if geometry != None:
        geometry = geometry.group(0)
    else:
        print('Dimensionality not found...')
        return None

    geometry = geometry.strip()
    geometry = geometry.split('\n')

    try:
        for i in range(len(geometry)):
            geometry[i] = geometry[i].strip()
            geometry[i] = geometry[i].split()
            for j in range(3, len(geometry[i])):
                geometry[i][j] = float(geometry[i][j])
    except Exception as e:
        print(e)
    return geometry


def read_and_write_infos(job):
    block = read_block(job)
    dimensionality = get_dimensionality(block)
    lattice_vector = get_lattice_vector(block)
    geometry = get_geometry(block)
    write_dimen(job, dimensionality)
    write_latt(job, lattice_vector)
    write_geometry(job, geometry)
    return dimensionality, lattice_vector, geometry


def creat_json_file(path):
    data = {'dimensionality': {}, 'lattice_vector': {}, 'geometry': {}}
    json_file = os.path.join(path, 'geometry.json')
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


def write_dimen(job, dimen):
    path = job.root_path
    path = os.path.join(path, 'cluster')
    json_file = os.path.join(path, 'geometry.json')
    with open(json_file, 'r') as f:
        data = json.load(f)
    x = job.x
    z = job.z
    x_and_z = '({}, {})'.format(x, z)
    dimen_data = data['dimensionality']
    dimen_data[x_and_z] = dimen
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


def write_latt(job, latt):
    path = job.root_path
    path = os.path.join(path, 'cluster')
    json_file = os.path.join(path, 'geometry.json')
    with open(json_file, 'r') as f:
        data = json.load(f)
    x = job.x
    z = job.z
    x_and_z = '({}, {})'.format(x, z)
    latt_data = data['lattice_vector']
    latt_data[x_and_z] = latt
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


def write_geometry(job, geo):
    path = job.root_path
    path = os.path.join(path, 'cluster')
    json_file = os.path.join(path, 'geometry.json')
    with open(json_file, 'r') as f:
        data = json.load(f)
    x = job.x
    z = job.z
    x_and_z = '({}, {})'.format(x, z)
    geo_data = data['geometry']
    geo_list = []
    for atom in geo:
        atom_dict = {}
        atom_dict['no'] = atom[0]
        atom_dict['nat'] = atom[1]
        atom_dict['ele'] = atom[2]
        atom_dict['x'] = atom[3]
        atom_dict['y'] = atom[4]
        atom_dict['z'] = atom[5]
        geo_list.append(atom_dict)
    geo_data[x_and_z] = geo_list
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)



















