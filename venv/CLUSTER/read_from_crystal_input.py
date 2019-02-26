#!/usr/bin/python3
import os
import math
from Data.Periodict_Table import periodic_table_rev
from Common import Point


def read_CrystalInput(file, transfer_fraction=False):
    if file[-5:] != 'INPUT':
        file = os.path.join(file, 'INPUT')
    with open(file) as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if len(line) > 0]
    point = 0
    while point < len(lines):
        if lines[point] == 'END':
            break
        point += 1
    lines = lines[:point]
    name = lines[0]
    type = lines[1]
    group = lines[2]
    lattice_para = lines[3].split()
    lattice_para = find_len_and_ang(lattice_para)
    number = int(lines[4])
    geometry = lines[5:5+number]
    geometry = transfer_GeoForm(geometry)
    if transfer_fraction == True:
        geometry = geo_transfer_from_fraction_to_angstrom(geometry, lattice_para)
    lattice_vec = transfer_LatticePara_to_LatticeVec(lattice_para, geometry)
    dimen = get_dimentionality(type)
    return dimen, lattice_vec, geometry


def get_dimentionality(type):
    type = type.upper()
    if type == 'SLAB':
        dimen = 2
    elif type == 'MOLECULE':
        dimen = 1
    else:
        dimen = 3
    return dimen


def transfer_GeoForm(geometry):
    geometry = [geo.split() for geo in geometry]
    count = 1
    for geo in geometry[:]:
        geo.insert(0, count)
        ele = periodic_table_rev[int(geo[1])]
        geo.insert(2, ele)
        geo[-1] = float(geo[-1])
        count += 1
    return geometry


def find_len_and_ang(LatticePara):
    LatticePara = [float(para) for para in LatticePara]
    length, angle = [], []
    if len(LatticePara) == 6:
        length = LatticePara[:3]
        angle = LatticePara[3:]
    elif len(LatticePara) == 3:
        length = LatticePara[:2]
        angle = LatticePara[2:]
    else:
        length = [para for para in LatticePara if para <= 30]
        angle = [para for para in LatticePara if para > 30]
    LatticePara = [length, angle]
    return LatticePara


# def transfer_LatticePara_to_LatticeVec(LatticePara, geometry):
#     # eckes = get_eckes(geometry)
#     # p1, p2, p3, p4, *_ = eckes
#     # v1 = point_minus(p1, p2)
#     length, angle = LatticePara
#     b = (0, length[1], 0)
#     if len(angle) == 1:
#         gama = angle[0]
#         a = (length[0] * math.sin(gama/180*math.pi), length[0] * math.cos(gama/180*math.pi), 0)
#         c = (0, 0, 500)
#     elif len(angle) == 3 and len(length) == 3:
#         gama = angle[-1]
#         beta = angle[-2]
#         alpha = angle[-3]
#         b = (length[1] * math.cos(gama/180*math.pi), length[1] * math.sin(gama/180*math.pi), 0)
#         c = (length[-1] * math.cos(beta/180*math.pi), length[-1]*math.cos(alpha/180*math.pi)*math.sin(gama/180*math.pi), math.sqrt((length[-1] * math.sin(beta/180*math.pi))**2 - (length[-1]*math.cos(alpha/180*math.pi)*math.sin(gama/180*math.pi))**2))
#     LatticeVec = [a, b, c]
#     return LatticeVec


def transfer_LatticePara_to_LatticeVec(LatticePara, geometry):
    # eckes = get_eckes(geometry)
    # p1, p2, p3, p4, *_ = eckes
    # v1 = point_minus(p1, p2)
    length, angle = LatticePara
    a = (length[0], 0, 0)
    if len(angle) == 1:
        gama = angle[0]
        b = (length[1] * math.cos(gama/180*math.pi), length[1] * math.sin(gama/180*math.pi), 0)
        c = (0, 0, 500)
    elif len(angle) == 3 and len(length) == 3:
        gama = angle[-1]
        beta = angle[-2]
        alpha = angle[-3]
        b = (length[1] * math.cos(gama/180*math.pi), length[1] * math.sin(gama/180*math.pi), 0)
        c = (length[-1] * math.cos(beta/180*math.pi), length[-1]*math.cos(alpha/180*math.pi)*math.sin(gama/180*math.pi), math.sqrt((length[-1] * math.sin(beta/180*math.pi))**2 - (length[-1]*math.cos(alpha/180*math.pi)*math.sin(gama/180*math.pi))**2))
    LatticeVec = [a, b, c]
    return LatticeVec


def point_minus(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    v = (x2-x1, y2-y1, z2-z1)
    return v


def get_eckes(geometry):
    x = [float(geo[-3]) for geo in geometry]
    y = [float(geo[-2]) for geo in geometry]
    z = [float(geo[-1]) for geo in geometry]
    x_min = min(x)
    x_max = max(x)
    y_min = min(y)
    y_max = max(y)
    z_min = min(z)
    z_max = max(z)
    p1 = (x_min, y_min, z_min)
    p2 = (x_max, y_min, z_min)
    p3 = (x_min, y_max, z_min)
    p4 = (x_max, z_max, z_min)
    p5 = (x_min, y_min, z_max)
    p6 = (x_max, y_min, z_max)
    p7 = (x_min, y_max, z_max)
    p8 = (x_max, z_max, z_max)
    eckes = [p1, p2, p3, p4, p5, p6, p7, p8]
    return  eckes


def cal_dis(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    dis = math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2) + ((z1 - z2) ** 2))
    return dis


def geo_transfer_from_fraction_to_angstrom(geometry, lattice_para):
    length, _ = lattice_para
    for geo in geometry:
        geo[-3] = float(geo[-3]) * length[0]
        geo[-2] = float(geo[-2]) * length[1]
    return geometry

# file = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\INPUT_full'
# read_CrystalInput(file, transfer_fraction=True)


















