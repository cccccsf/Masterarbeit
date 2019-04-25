#!/usr/bin/python3
import os
import csv
import json
from Correction.read_results import is_number


def record_data_json(Res, item, json_file, init_distance=3.1):
    job = Res.job
    path = Res.path
    energy = Res.energy
    unit = Res.unit
    basis_set = None
    try:
        basis_set = Res.bs
    except:
        pass
    coord = '{}'.format(job.coord)
    x = job.x
    if is_number(x):
        x = float(x)
    z = job.z
    if is_number(z):
        z = float(z) + init_distance
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        creat_json_file(json_file)
        with open(json_file, 'r') as f:
            data = json.load(f)
    if coord not in data:
        data[coord] = {}
    if basis_set != None:
        data[coord][item] = {
            'energy': energy,
            'unit': unit,
            'x': x,
            'z': z,
            'basis set': basis_set,
            'path': path
        }
    else:
         data[coord][item] = {
            'energy': energy,
            'unit': unit,
            'x': x,
            'z': z,
            'path': path
        }
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)



def creat_json_file(json_file):
    info_json = {}
    with open(json_file, 'w') as f:
        json.dump(info_json, f, indent=4)
