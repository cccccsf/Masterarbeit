#!/usr/bin/python3
import os
import json

def read_init_dis(path):
    json_file = os.path.join(path, 'opt_geo_and_latt.json')
    with open(json_file, 'r') as f:
        data = json.load(f)
    init_dist = data['init_dist']
    init_dist = float(init_dist)
    return init_dist



# path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test'
# read_init_dis(path)
