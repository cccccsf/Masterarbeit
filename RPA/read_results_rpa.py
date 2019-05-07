#!/usr/bin/python3
import os
import re
from Common import Job
from Common import read_all_results


def get_energy(path):
    if type(path) == Job:
        path = path.path
    path = os.path.join(path, 'rpa.out')
    with open(path, 'rb') as f:
        f.seek(-20000, 2)
        lines = f.read().decode('utf-8')
    regex = 'LRPA correlation energy.*?\n'
    energy = re.search(regex, lines, re.M|re.S)
    if energy != None:
        energy = energy.group(0)
    else:
        print(path)
        print('Energy infomation not found...')

    energy = energy.strip()
    energy = energy.split()
    energy = energy[-1]

    return energy



def read_and_record_all_results(jobs):
    read_all_results(jobs, 'rpa', energy_func=get_energy)
