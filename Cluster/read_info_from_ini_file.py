#!/usr/bin/python3
import sys
import math
import configparser
from Data import periodic_table_rev


class GeoIniReader(object):

    def __init__(self, file):
        self.file = file
        self.cfg = configparser.ConfigParser()
        self.read_ini_file()

        self.dimensionality = self.read_dimensionality()
        self.if_fraction_transform = self.get_if_fraction_transform()
        self.lattice_vector = self.read_lattice_vector()
        self.lattice_parameter = self.get_lattice_parameters()
        self.geometry = self.read_geometry()

    def read_ini_file(self):
        try:
            self.cfg.read(self.file, encoding='utf-8')
        except Exception as e:
            print(e)

    def read_geometry(self):
        options = self.cfg.options('geometry')
        atomsOpt = [opt for opt in options if opt.startswith('atom')]
        geometry = [self.cfg.get('geometry', opt) for opt in atomsOpt]
        geometry = [geo.split() for geo in geometry]
        geometry = self.add_element_geometry(geometry)
        if self.if_fraction_transform is True:
            geometry = self.geo_transfer_from_fraction_to_angstrom(geometry)
        return geometry

    def get_if_fraction_transform(self):
        try:
            self.if_fraction_transform = self.cfg.get('geometry', 'fraction_transform')
            assert isinstance(self.if_fraction_transform, str)
            if self.if_fraction_transform.lower() == 'true':
                self.if_fraction_transform = True
            else:
                self.if_fraction_transform = False
        except configparser.NoOptionError:
            self.if_fraction_transform = False
        return self.if_fraction_transform

    @staticmethod
    def add_element_geometry(geometry):
        count = 1
        for geo in geometry:
            nat = int(geo[0])
            element = periodic_table_rev[nat]
            geo.insert(0, count)
            geo.insert(2, element)
            count += 1
        return geometry

    def read_dimensionality(self):
        try:
            dimen = self.cfg.get('dimensionality', 'dimensionality')
        except configparser.NoSectionError or configparser.NoOptionError:
            dimen = 2
        return dimen

    def read_lattice_vector(self):
        try:
            a = self.cfg.get('lattice vector', 'a')
            b = self.cfg.get('lattice vector', 'b')
            c = self.cfg.get('lattice vector', 'c')
            a = [float(a) for a in a.split()]
            b = [float(b) for b in b.split()]
            c = [float(c) for c in c.split()]
            lv = [a, b, c]
        except configparser.NoOptionError:
            try:
                options = self.cfg.options('lattice vector')
                a = self.cfg.get('lattice vector', options[0])
                b = self.cfg.get('lattice vector', options[1])
                c = self.cfg.get('lattice vector', options[2])
                a = [float(a) for a in a.split()]
                b = [float(b) for b in b.split()]
                c = [float(c) for c in c.split()]
                lv = [a, b, c]
            except Exception as e:
                print(e)
                print('Please enter lattice vector with \'a=\', \'b=\' and \'c=\' in geo.ini . ')
                sys.exit()
        return lv

    def geo_transfer_from_fraction_to_angstrom(self, geometry):
        """
        When the x and y coordinates of the geometry is with fraction unit,
        transfer it to ordinary length unit

        """
        a, b, _ = self.lattice_parameter
        for geo in geometry:
            geo[-3] = float(geo[-3]) * a
            geo[-2] = float(geo[-2]) * b
        return geometry

    def get_lattice_parameters(self):
        a, b, c = self.lattice_vector
        a = math.sqrt(sum([i**2 for i in a]))
        b = math.sqrt(sum([i**2 for i in b]))
        c = math.sqrt(sum([i**2 for i in c]))
        return [a, b, c]

    def get_infos(self):
        return self.dimensionality, self.lattice_vector, self.geometry

