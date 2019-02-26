#!/usr/bin/python3
from Data.Periodict_Table import periodic_table_rev

class Atom(object):

    def __init__(self, nat, x, y, z, no=1, type=1, coor=1, coor_vec=[]):
        self.nat = nat
        self.element = periodic_table_rev[int(nat)]
        self.x = x
        self.y = y
        self.z = z
        self.no = no
        self.type =type
        self.coor = coor
        self.coor_vec = coor_vec
        self.coor_vec_free = []

    def __repr__(self):
        return self.nat.center(10) + ' ' + '{:.12E}'.format(float(self.x)).rjust(19) + ' ' + '{:.12E}'.format(float(self.y)).rjust(19) + ' ' + '{:.12E}'.format(float(self.z)).rjust(19)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __setitem__(self, key, value):
        self._item[index] = value
