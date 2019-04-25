#!/usr/bin/python3
import os
import sys
import json
import Results
from Correction import Result
from Results import calculation
from copy import deepcopy


class CorrectionResult(Result):

    def __init__(self, job, unit_type='Hartree'):
        super(CorrectionResult, self).__init__(job, unit_type)
        self.results_file = self.get_results_file()
        self.coord = str(self.job.coord)
        self.energy, self.unit = self.read_energy()

    def __repr__(self):
        return '{}: {} {}'.format(self.coord, self.energy, self.unit)

    def read_energy(self):
        try:
            with open(self.results_file, 'r') as f:
                data = json.load(f)
            data = data[self.coord][self.method]
            energy, unit = data['energy'], data['unit']
        except FileNotFoundError:
            print('File results.json not found.')
            print('Please check the programm and the pragramm will exit. ')
            sys.exit()
        except KeyError:
            print(self.job)
            print('Result not in results.json found.')
            print(
                'Programm will read the energy from output file.\n'
                'If you want to record the calculation result into the results.json file, '
                'Please move the file to another directory and run this step again.')
            self.get_energy()
            self.unit_transform()
            energy, unit = self.energy, self.unit
        return energy, unit


    def get_results_file(self):
        cluster_path = os.path.join(self.job.root_path, 'cluster')
        results_file = os.path.join(cluster_path, 'results.json')
        return results_file


    def set_extrapolation_energy(self, Res1, Res2, X=[2, 3]):
        assert type(Res1) == Results.correction_data_process.CorrectionResult
        assert type(Res2) == Results.correction_data_process.CorrectionResult
        if Res1.unit != Res2.unit:
            Res2.unit = Res1.unit
            Res2.unit_type = Res1.unit
            Res2.unit_transform()
        e1 = Res1.energy
        e2 = Res2.energy
        x, y = X
        e = calculation.get_extrapolated_correction(e1, e2, x, y)
        self.energy = e
        self.unit = Res1.unit

    def __sub__(self, other):
        assert type(other) == Results.correction_data_process.CorrectionResult
        if other.unit != self.unit:
            other.unit_type = self.unit
            other.unit_transform()
        new_Res = deepcopy(self)
        new_Res.energy = self.energy - other.energy
        return new_Res

    def __add__(self, other):
        if type(other) == CorrectionResult:
            if other.unit != self.unit:
                other.unit_type = self.unit
                other.unit_transform()
            new_Res = deepcopy(self)
        elif type(other) == Results.FResult:
            if other.unit != self.unit:
                other.set_unit(self.unit)
            new_Res = deepcopy(other)
        new_Res.energy = self.energy + other.energy
        return new_Res
