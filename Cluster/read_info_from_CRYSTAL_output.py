#!/usr/bin/python3
import os
import re


def read_info_block(out_file):
    size = os.path.getsize(out_file)
    s = -int(size/10)
    with open(out_file, 'rb') as f:
        f.seek(s, 2)
        out = f.read().decode('utf-8')
    # search final optimized geometry
    reg = 'FINAL OPTIMIZED GEOMETRY.*'
    block = re.search(reg, out, re.M | re.S)
    if block is not None:
        block = block.group(0)
    else:
        print('Information not found.')
        return None
    return block


def get_dimensionality(block):

    reg = 'FINAL OPTIMIZED GEOMETRY.*?\n'
    dimen = re.search(reg, block, re.M|re.S)
    if dimen is not None:
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
    if latt_vec is not None:
        latt_vec = latt_vec.group(0)
    else:
        print('Lattice Vector not found...')
        return None
    latt_vec = latt_vec.strip('\n')
    latt_vec = latt_vec.split('\n')
    latt_vec = latt_vec[-3:]
    try:
        for i in range(len(latt_vec)):
            latt_vec[i] = latt_vec[i].strip().split()
            for j in range(len(latt_vec[i])):
                latt_vec[i][j] = float(latt_vec[i][j])
    except Exception as e:
        print(e)
        print('Can not found lattice vector...')
        return None
    return latt_vec


def get_geometry(block):

    reg = 'CARTESIAN COORDINATES.*?\n\n'
    geo = re.search(reg, block, re.M|re.S)
    if geo is not None:
        geo = geo.group(0)
    else:
        print('Geometry not found...')
        return None

    reg = '    1.*\n\n'
    geometry = re.search(reg, geo, re.M|re.S)
    if geometry is not None:
        geometry = geometry.group(0)
    else:
        print('Geometry not found...')
        return None

    reg = '   [0-9].*'
    geometry = geometry.rstrip()
    geometry = re.findall(reg, geometry)

    try:
        for i in range(len(geometry)):
            geometry[i] = geometry[i].strip()
            geometry[i] = geometry[i].split()
            for j in range(3, len(geometry[i])):
                geometry[i][j] = float(geometry[i][j])
        geometry = [atom for atom in geometry if len(atom) > 3]
    except Exception as e:
        print(e)
    return geometry


def read_info(out_file):
    try:
        block = read_info_block(out_file)
        dimensionality = get_dimensionality(block)
        lattice_vector = get_lattice_vector(block)
        geometry = get_geometry(block)
        return dimensionality, lattice_vector, geometry
    except FileNotFoundError as e:
        print('Output file not found.')
        return None, None, None


