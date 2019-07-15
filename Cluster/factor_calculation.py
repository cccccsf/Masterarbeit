#!/usr/bin/python3
import math
from Cluster import Atom



class FactorCalculator(object):


    def __init__(self, cluster):
        self.cluster = cluster
        self.dimen = self.cluster.dimensionality
        self.center, self.UpperCenter, self.UnderCenter = cluster.centre, cluster.UpperCenter, cluster.UnderCenter
        self.lattice_vector = self.cluster.lattice_vector
        self.l, self.l1, self.l2, self.l3 = cluster.l, cluster.l1, cluster.l2, cluster.l3
        # print(self.center)
        # print(self.lattice_vector)
        # print('l:', self.l, self.l1, self.l2, self.l3)

    def get_distance_to_center(self, atom, layer='', factor=False):
        
        if type(atom) == Atom:
            x, y, z = atom.x, atom.y, atom.z
        else:
            x, y, z = atom

        if layer == 'under':
            center = self.UnderCenter
        elif layer == 'upper':
            center = self.UpperCenter
        else:
            center = self.center

        if self.dimen == 2:
            x0, y0 = center
            dis = math.sqrt((x-x0)**2 + (y-y0)**2)
            print('The distance between the given atom and the central axis is: ', dis)
        else:
            x0, y0, z0 = center
            dis = math.sqrt((x-x0)**2 + (y-y0)**2 + (z-z0)**2)
            print('The distance between the given atom and the central point is: ', dis)
        
        if factor == True:
            return round(dis/self.l, 2)
        else:
            return dis

    def get_distance_to_vector(self, atom, vec, layer='', factor=False):

        if type(vec) == tuple and len(vec) == 3:
            vx, vy, vz = vec
            l = math.sqrt(vx**2 + vy**2 + vz**2)
        elif vec in ['a', 'b', 'c'] or int(vec) in [1, 2, 3] or vec in ['x', 'y' 'z']:
            if vec == 'a' or vec == 'x' or int(vec) == 1:
                vector = self.lattice_vector[0]
                l = self.l1
            elif vec == 'b' or vec == 'y' or int(vec) == 2:
                vector = self.lattice_vector[1]
                l = self.l2
            elif vec == 'c' or vec == 'z' or int(vec) == 3:
                vector = self.lattice_vector[2]
                l = self.l3
        vx, vy, vz = vector

        if type(atom) == Atom:
            x, y, z = atom.x, atom.y, atom.z
        else:
            x, y, z = atom

        if layer == 'under':
            center = self.UnderCenter
        elif layer == 'upper':
            center = self.UpperCenter
        else:
            center = self.center
        
        if self.dimen == 2:
            cx, cy = center
            ux = x - cx
            uy = y - cy
            proj = (ux*vx + uy*vy) / math.sqrt(vx**2 + vy**2)
        else:
            cx, cy, cz = center
            ux = x - cx
            uy = y - cy
            uz = z - cz
            proj = (ux*vx + uy*vy + uz*vz) / math.sqrt(vx**2 + vy**2 + yz**2)
        
        if factor == True:
            return round(proj/l, 2)
        else:
            return proj
