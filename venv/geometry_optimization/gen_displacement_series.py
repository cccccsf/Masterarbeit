#!/usr/bin/python3

fibo_num = [1, 2, 3, 5, 8, 13]

class Range_of_Distances(object):

    def __init__(self, geometry_info, fixed_atoms):
        self.geometry_info = geometry_info
        self.__upper_layer = []
        self.__under_layer =[]
        self.fixed_atoms = fixed_atoms
        self.init_distance = 0
        self.distances = []
        self.delta_distances = []
        self.z_fixed_atoms = []

    def transfer_to_float(self):
        new_geo = []
        for atom in self.geometry_info:
            new_atom = []
            for unit in atom:
                new_unit = float(unit)
                new_atom.append(new_unit)
            new_geo.append(new_atom)
        #print(new_geo)
        return new_geo

    def gen_fixed_atoms(self):
        count = 1
        geo_info_with_number = self.geometry_info
        for atom in geo_info_with_number:
            new_atom = []
            for unit in atom:
                new_atom.append(float(unit))
            geo_info_with_number.append(new_atom)
        for atom in geo_info_with_number:
            atom.insert(0, count)
            count += 1
        z_coordinates = []
        z_coordinates_with_num = {}
        z_coordinates_with_num_re = {}
        for atom in geo_info_with_number:
            z_coordinates_with_num[atom[0]] = atom[4]
            z_coordinates_with_num_re[atom[4]] = atom[0]
            z_coordinates.append(atom[4])
        z_coordinates.sort()
        #for i in range(1, len(z_coordinates)):
        i = 1
        while i < len(z_coordinates):
            if abs(z_coordinates[i] - z_coordinates[i-1]) < 0.2:
                z_coordinates.pop(i)
            else:
                i += 1
        distance = 0
        z_fixed_atoms = []
        for i in range(1, len(z_coordinates)):
            if (abs(z_coordinates[i] - z_coordinates[i-1])) > distance:
                distance = abs(z_coordinates[i] - z_coordinates[i-1])
                z_fixed_atoms.append(z_coordinates[i])
                z_fixed_atoms.append(z_coordinates[i-1])
        n_fixed_atoms = []
        n_fixed_atoms.append(z_coordinates_with_num_re[z_fixed_atoms[0]])
        n_fixed_atoms.append(z_coordinates_with_num_re[z_fixed_atoms[1]])
        #return n_fixed_atoms
        self.fixed_atoms = z_fixed_atoms
        self.init_distance = distance
        #print(self.fixed_atoms)
        #print(self.init_distance)

    def get_z_fixed_atoms(self):
        self.z_fixed_atoms.append(self.geometry_info[(int(self.fixed_atoms[0])-1)][3])
        self.z_fixed_atoms.append(self.geometry_info[(int(self.fixed_atoms[1])-1)][3])

    def get_two_layers(self):
        for atom in self.geometry_info:
            if atom[3] >= max(self.z_fixed_atoms):
                self.__upper_layer.append(atom)
            elif atom[3] <= min(self.z_fixed_atoms):
                self.__under_layer.append(atom)
        #print(self.__upper_layer)
        self.init_distance = abs(self.z_fixed_atoms[0] - self.z_fixed_atoms[1])
        #print(self.init_distance)

    def get_max_atom_distance(self, geo):
        z_coordinates = []
        #print(geo)
        for atom in geo:
            z_coordinates.append(atom[3])
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
            delta_dist_forward.append(accum)
        accum_1 = 0
        for i in fibo_num[1:4]:
            dist = -(min_delta_dist * (i / sum_backward))
            accum_1 = dist + accum_1
            delta_dist_backward.append(accum_1)
        self.delta_distances = delta_dist_backward + delta_dist_forward
        #print(self.delta_distances)
        self.distances = [(self.init_distance + delta) for delta in self.delta_distances]
        self.distances.sort()
        #print(self.distances)

    def get_diff_geometry(self):
        new_geometrys = []
        new_upper_layer = self.__upper_layer
        z_coord = []
        for atom in self.__upper_layer:
            z = atom[3]
            z_coord.append(z)
        for dist in self.delta_distances:
            i = 0
            while i < len(self.__upper_layer):
                #print(z_coord[i])
                new_atom_z = z_coord[i] + dist
                #print(new_atom_z)
                new_upper_layer[i][3] = new_atom_z
                i += 1
            new_geometry = new_upper_layer + self.__under_layer
            new_geometrys.append(new_geometry)
        return new_geometrys

    def get_geo_series(self):
        # print(self.geometry_info)
        self.geometry_info = self.transfer_to_float()
        self.get_z_fixed_atoms()
        self.get_two_layers()
        upper_atom_dist = self.get_max_atom_distance(self.__upper_layer)
        under_atom_dist = self.get_max_atom_distance(self.__under_layer)
        max_atom_dist = max(upper_atom_dist, under_atom_dist)
        self.get_distance_series(max_atom_dist)
        new_geometrys = self.get_diff_geometry()
        dict_new_geometrys = dict(zip(self.delta_distances, new_geometrys))
        return dict_new_geometrys


class Range_of_Displacement(Range_of_Distances):
    def __init__(self, geometry_info, fixed_atoms):
        super().__init__(geometry_info, fixed_atoms)
        self.__upper_layer = []
        self.__under_layer =[]
        #self.delta_displacement = [-0.5, -0.4, -0.3, -0.15, 0.1, 0.25, 0.35, 0.5]
        self.delta_displacement = [0.1, 0.25, 0.35, 0.5]
        self.fixed_atoms = fixed_atoms

    def gen_two_layers(self):
        for atom in self.geometry_info:
            if atom[3] >= max(self.z_fixed_atoms):
                self.__upper_layer.append(atom)
            elif atom[3] <= min(self.z_fixed_atoms):
                self.__under_layer.append(atom)
        #print(self.__upper_layer)
        self.init_distance = abs(self.z_fixed_atoms[0] - self.z_fixed_atoms[1])

    def get_new_geometrys(self):
        new_geometrys = []
        new_upper_layer = self.__upper_layer
        x_coord = []
        for atom in self.__upper_layer:
            x = atom[1]
            x_coord.append(x)
        for displace in self.delta_displacement:
            i = 0
            #print(displace)
            while i < len(self.__upper_layer):
                new_x = x_coord[i] + displace
                #print(x_coord[i])
                new_upper_layer[i][1] = new_x
                i += 1
                #print(new_x)
            new_geometry = new_upper_layer + self.__under_layer
            new_geometrys.append(new_geometry)
        return new_geometrys

    def get_geometry_series(self):
        self.geometry_info = self.transfer_to_float()
        self.get_z_fixed_atoms()
        self.gen_two_layers()
        #print(self.__upper_layer)
        new_geometrys = self.get_new_geometrys()
        #print(new_geometrys)
        dict_new_geometrys = dict(zip(self.delta_displacement, new_geometrys))
        return dict_new_geometrys





