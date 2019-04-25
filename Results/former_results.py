#!/usr/bin/python3
import os
import sys
import json
from copy import deepcopy
from Common import is_number
from Results import CorrectionResult


class FResult(object):

    def __init__(self, job):
        self.job = job
        self.path = job.path
        self.method = job.method
        self.layertype = job.layertype
        self.energy = None
        self.unit = 'hartree'
        self.x, self.z = 0, 0
        self.original_json_file = self.get_original_json_file()
        self.coord = str(self.job.coord)


    def read_info_from_json(self):
        try:
            with open(self.original_json_file, 'r') as f:
                data = json.load(f)
            data = data[self.coord]
            data = data[self.layertype]
            self.x = data['x']
            self.z = data['z']
            self.energy = data['energy']
            if is_number(self.energy):
                self.energy = float(self.energy)
        except FileNotFoundError:
            print(self.job)
            print(self.original_json_file)
            print('json file not found')
            print('Please check it and restart the programm.')
            sys.exit()

    def get_original_json_file(self):
        path = self.job.root_path
        path = os.path.join(path, self.method)
        json_file = os.path.join(path, '{}.json'.format(self.method))
        return json_file

    def set_unit(self, unit='Hartree'):
        """
        tranform unit
        :param unit: unit which you want to transform to
                     unit can be transformed is listed as following:
                     hartree, eV, cm, kcal/mol, kj/mol, k, Hz
        :return:
        """
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
        unit = unit.lower()
        if unit not in unit_dict:
            print('Unit not found in unit dict.')
            print('Unit transform will not continue.')
        else:
            unit_from = unit_dict[self.unit]
            unit_to = unit_dict[unit]
            coe = unit_to/unit_from
            self.energy = self.energy * coe
            self.unit = unit

    def __sub__(self, other):
        if other.unit != self.unit:
            other.set_unit(self.unit)
        new_FR = deepcopy(self)
        new_FR.energy = self.energy - other.energy
        return new_FR

    def __add__(self, other):
        if type(other) == FResult:
            if other.unit != self.unit:
                other.set_unit(self.unit)
            new_FR = deepcopy(self)
        elif type(other) == CorrectionResult:
            if other.unit != self.unit:
                other.unit_type = self.unit
                other.unit_transform()
            new_FR = deepcopy(self)
        new_FR.energy = self.energy + other.energy
        return new_FR

    def __repr__(self):
        return '{}: {} {}'.format(self.coord, self.energy, self.unit)

    def record_data(self, item, json_file=None):
        if json_file == None:
            json_file = self.original_json_file
        if not os.path.exists(json_file):
            data = {}
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            coord = str(self.coord)
            if coord not in data:
                data[coord] = {}
            datum = data[coord]
            datum[item] = {
                'energy': self.energy,
                'unit': self.unit,
                'x': self.x,
                'z': self.z,
                'path': self.path
            }
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
        except FileNotFoundError:
            pass
