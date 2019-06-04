#!/usr/bin/python3
import os
import re
import csv
import json
from Common import rename_file


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


class Result(object):

    def __init__(self, job, unit_type='Hartree'):
        self.job = job
        self.path = job.path
        self.method = job.method
        self.step = self.get_step()
        self.bs = self.get_bs_type()
        self.energy, self.unit = None, None
        self.unit_type = unit_type

    def get_method_error(self):
        out_file = os.path.join(self.path, self.job.method) + '.out'
        with open(out_file, 'rb') as f:
            f.seek(-20000, 2)
            text = f.read().decode('utf-8')
        pattern = 'DELTA_DE_LCCSDT_RPA.*?\n'
        energy = re.search(pattern, text)
        if energy is not None:
            energy = energy.group(0)
            energy = energy.strip()
            energy = energy.split()
            if is_number(energy[-1]):
                unit = 'Hartree'
                energy = float(energy[-1])
            elif is_number(energy[-2]):
                unit = energy[-1].lower()
                energy = float(energy[-2])
            else:
                print(self.job)
                print('Energy infomation not found...')
                print('Please check the output file.')
                energy, unit = None, None
        else:
            print(self.job)
            print('Energy infomation not found...')
            print('Please check the output file.')
            unit = None
        return energy, unit

    def get_step(self):
        step = self.method.split('_')
        step = step[1:]
        step = '_'.join(step)
        return step

    def get_bs_type(self):
        bs = self.method.split('_')[0]
        bs_set = {'avdz', 'avtz', 'avqz'}
        if bs == 'per':
            bs = 'per'
        return bs

    def get_e_iext1_rpa(self):
        out_file = os.path.join(self.path, self.job.method) + '.out'
        with open(out_file, 'rb') as f:
            f.seek(-20000, 2)
            text = f.read().decode('utf-8')
        pattern = 'DE_LRPA.*?\n'
        unit = None
        energy = re.search(pattern, text)
        if energy is not None:
            energy = energy.group(0)
            energy = energy.strip()
            energy = energy.split()
            if is_number(energy[-1]):
                unit = 'Hartree'
                energy = float(energy[-1])
            elif is_number(energy[-2]):
                unit = energy[-1].lower()
                energy = float(energy[-2])
            else:
                print(self.job)
                print('Energy infomation not found...')
                print('Please check the output file.')
                energy = None
        else:
            print(self.job)
            print('Energy infomation not found...')
            print('Please check the output file.')
        return energy, unit

    def get_energy(self):
        if self.step == 'rpa_cc':
            self.energy, self.unit = self.get_method_error()
        else:
            self.energy, self.unit = self.get_e_iext1_rpa()

    def unit_transform(self):
        unit_dict = {
            'ha': 1,
            'hartree': 1,
            'ev': 27.2113839,
            'cm': 219474.63067,
            'kcal/mol': 627.5096,
            'kj/mol': 2625.50,
            'k': 3.157747E5,
            'hz': 6.5796839207E15
        }
        self.unit_type = self.unit_type.lower()
        if self.unit is None:
            print(self.job, ':')
            print('unit not Found.')
        elif self.unit.lower() not in unit_dict or self.unit_type not in unit_dict:
            print(self.job, ':')
            print('unit not found in our unit dictionary.')
            print('unit transform will not continue.')
        else:
            unit_from = unit_dict[self.unit]
            unit_to = unit_dict[self.unit_type]
            coe = unit_to / unit_from
            self.energy = self.energy * coe
            self.unit = self.unit_type


def read_all_results(jobs, init_distance=0):
    Results = []
    for job in jobs:
        Res = Result(job)
        Res.get_energy()
        # print(job)
        # print(Res.energy, Res.unit)
        Res.unit_transform()
        Results.append(Res)
    record_all_results_into_json(Results, init_distance)
    record_all_results_into_csv(Results, init_distance)


def record_all_results_into_json(Results, init_distance):
    assert len(Results) != 0
    path = Results[0].job.root_path
    path = os.path.join(path, 'cluster')
    json_file = os.path.join(path, 'correction.json')
    creat_json_file(json_file)
    for Res in Results:
        record_to_json_each_data(Res, init_distance, json_file)


def record_to_json_each_data(Res, init_distance, json_file):
    job = Res.job
    path = Res.path
    method = Res.method
    energy = Res.energy
    unit = Res.unit
    basis_set = Res.bs
    coor = '{}'.format(job.coord)
    x = job.x
    if is_number(x):
        x = float(x)
    z = job.z
    if is_number(z):
        z = float(z) + init_distance
    with open(json_file, 'r') as f:
        data = json.load(f)
    if coor not in data:
        data[coor] = {}
    data[coor][method] = {
        'energy': energy,
        'unit': unit,
        'x': x,
        'z': z,
        'basis set': basis_set,
        'path': path
    }
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


def creat_json_file(json_file):
    info_json = {}
    # print(json_file)
    with open(json_file, 'w') as f:
        json.dump(info_json, f, indent=4)


def record_all_results_into_csv(Results, init_distace):
    assert len(Results) != 0
    path = Results[0].job.root_path
    csv_file = os.path.join(path, 'correction.csv')
    rename_file(path, 'correction.csv')
    creat_csv_file(csv_file)
    try:
        Results.sort(key=lambda x: x.job.x)
    except BaseException:
        pass
    for Res in Results:
        write_csv_each_data(Res, csv_file, init_distace)


def write_csv_each_data(Res, csv_file, init_distace):
    job = Res.job
    method = Res.method
    energy = Res.energy
    unit = Res.unit
    basis_set = Res.bs
    coor = '{}'.format(job.coord)
    x, z = job.x, job.z
    if is_number(x):
        x = float(x)
    if is_number(z):
        z = float(z) + init_distace
    try:
        new_line = [
            str(x),
            str(z),
            str(method),
            str(basis_set),
            str(energy),
            str(unit)]
        with open(csv_file, 'a', newline='') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(new_line)
    except Exception as e:
        print(e)


def creat_csv_file(csv_file):
    headers = [
        'displacement',
        'distance(A)',
        'method',
        'basis set',
        'E',
        'unit']
    with open(csv_file, 'w', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
