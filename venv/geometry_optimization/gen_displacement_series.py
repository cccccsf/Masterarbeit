#!/usr/bin/python3
from Crystal import Geometry
from copy import deepcopy

fibo_num = [1, 2, 3, 5, 8, 13]

class Range_of_Distances(object):

    def __init__(self, geometry, job):
        self.geometry = geometry
        self.upper_layer = []
        self.under_layer =[]
        self.init_distance = 0
        self.distances = []
        self.delta_distances = []


    def get_two_layers(self):
        z_fixed = []
        z_fixed.append(float(self.geometry.z_fixed_co[0]))
        z_fixed.append(float(self.geometry.z_fixed_co[1]))
        for i in range(len(self.geometry.z)):
            z = float(self.geometry.z[i])
            if z >= max(z_fixed):
                self.upper_layer.append(self.geometry[i])
            elif z <= min(z_fixed):
                self.under_layer.append(self.geometry[i])
        self.init_distance = self.geometry.layer_distance
        # print(self.__upper_layer)
        # print(self.__under_layer)
        # print(self.init_distance)


    def get_max_atom_distance(self, geo):
        z_coordinates = []
        #print(geo)
        for atom in geo:
            z_coordinates.append(float(atom[4]))
        i = 1
        while i < len(z_coordinates):
        #for i in range(1, len(z_coordinates)):
            if abs(z_coordinates[i] - z_coordinates[i-1]) < 0.2:
                    z_coordinates.pop(i)
            else:
                i += 1
        distance = 0
        for i in range(1, len(z_coordinates)):
            if (abs(z_coordinates[i] - z_coordinates[i-1])) > distance:
                distance = abs(z_coordinates[i] - z_coordinates[i-1])
        return distance


    def get_distance_series(self, min_dist):
        max_delta_dist = 2 * self.init_distance
        max_dist = self.init_distance + max_delta_dist
        min_delta_dist = self.init_distance - min_dist
        sum_forward = sum(fibo_num[:5])
        sum_backward = sum(fibo_num[1:5])
        dist = 0
        delta_dist_forward = []
        delta_dist_backward = []
        accum = 0
        for i in fibo_num[:5]:
            dist = max_delta_dist * (i / sum_forward)
            accum = dist + accum
            accum = round(accum, 12)
            delta_dist_forward.append(accum)
        accum_1 = 0
        for i in fibo_num[1:4]:
            dist = -(min_delta_dist * (i / sum_backward))
            accum_1 = dist + accum_1
            accum_1 = round(accum_1, 12)
            delta_dist_backward.append(accum_1)
        self.delta_distances = delta_dist_backward + delta_dist_forward
        #print(self.delta_distances)
        self.distances = [(self.init_distance + delta) for delta in self.delta_distances]
        self.distances.sort()
        #print(self.distances)


    def get_diff_geometry(self):
        new_geometrys = []
        new_geometrys_dict = {}
        z_coord = []
        for atom in self.upper_layer:
            z = float(atom[4])
            z_coord.append(z)
        for dist in self.delta_distances:
            new_upper_layer = deepcopy(self.upper_layer)
            for  i in range(len(self.upper_layer)):
                new_atom_z = z_coord[i] + dist
                new_atom_z = round(new_atom_z, 12)
                new_upper_layer[i][4] = new_atom_z
            new_geometry = new_upper_layer + self.under_layer
            new_geometry = Geometry(geometry=new_geometry)
            new_geometrys.append(new_geometry)
            new_geometrys_dict[dist] = new_geometry
        return new_geometrys_dict

    def get_geo_series(self):
        self.get_two_layers()
        upper_atom_dist = self.get_max_atom_distance(self.upper_layer)
        under_atom_dist = self.get_max_atom_distance(self.under_layer)
        max_atom_dist = max(upper_atom_dist, under_atom_dist)
        self.get_distance_series(max_atom_dist)
        new_geometrys_dict = self.get_diff_geometry()
        return new_geometrys_dict



class Range_of_Displacement(Range_of_Distances):
    def __init__(self, geometry, job):
        super().__init__(geometry, job)
        #self.delta_displacement = [-0.5, -0.4, -0.3, -0.15, 0.1, 0.25, 0.35, 0.5]
        self.delta_displacement = [0.1, 0.25, 0.35, 0.5]


    def get_new_geometrys(self):
        new_geometrys = []
        new_geometrys_dict = {}
        x_coord = []
        for atom in self.upper_layer:
            x = float(atom[2])
            x_coord.append(x)
        for displace in self.delta_displacement:
            new_upper_layer = deepcopy(self.upper_layer)
            for i in range(len(self.upper_layer)):
                new_x = x_coord[i] + displace
                new_upper_layer[i][2] = new_x
            new_geometry = new_upper_layer + self.under_layer
            new_geometry = Geometry(geometry=new_geometry)
            new_geometrys.append(new_geometry)
            new_geometrys_dict[displace] = new_geometry
        return new_geometrys_dict


    def get_geo_series(self):
        self.get_two_layers()
        new_geometrys_dict = self.get_new_geometrys()
        return new_geometrys_dict





