#!/usr/bin/python3

from copy import deepcopy

class Geometry(object):

    def __init__(self, init_path = '', geometry = [], fixed_atoms = [], json_form = []):
        self.elements = []
        self.x = []
        self.y = []
        self.z = []
        self.no = []
        self.geometry = geometry

        self.init_path = init_path
        self.json_form = json_form
        if self.json_form != []:
            self.init_geo_from_json()
        else:
            self.read_geometry(init_path)
            self.collect_geometry()

        self.number_of_atoms = len(self.geometry)
        self.layer_distance = 0
        self.z_fixed_no = [0, 0]
        self.z_fixed_co = [0, 0]
        self.z_free_no = []
        self.get_layerdistance()

        if fixed_atoms != []:
            self.set_fixed_atoms(fixed_atoms)


    def __len__(self):
        return len(self.geometry)

    def __repr__(self):
        string = ''
        for element in self.geometry:
            line = element[1].center(11) + ' ' + '{:.12E}'.format(float(element[2])).rjust(19) + ' ' + str(element[3]).rjust(19) + ' ' + '{:.12E}'.format(float(element[4])).rjust(19)
            string = string + line + '\n'
        return string

    def __getitem__(self, key):
        return self.geometry[key]

    def __iter__(self):
        return iter(self.geometry)

    def collect_geometry(self):
        if self.geometry == []:
            l = len(self.elements)
            count = 1
            for i in range(l):
                line = []
                line.append(count)
                self.no.append(count)
                line.append(self.elements[i])
                line.append(self.x[i])
                line.append(self.y[i])
                line.append(self.z[i])
                self.geometry.append(line)
                count += 1
        else:
            pass

    def read_geometry(self, path):
        if self.geometry == []:
            if path != '':
                with open(path + '/optimized_geometry', 'r') as f:
                    lines = f.read()
                lines = lines.split('\n')
                i = 0
                for line in lines:
                    if line == '':
                        del lines[i]
                    else:
                        i += 1
                for line in lines:
                    line = line.strip()
                    line = line.split(' ')
                    self.elements.append(line[0])
                    self.x.append(line[1])
                    self.y.append(line[2])
                    self.z.append(line[3])
            else:
                pass
        else:
            for i in range(len(self.geometry)):
                if len(self.geometry[i]) == 4:
                    self.geometry[i].insert(0, (i+1))
                self.elements.append(self.geometry[i][1])
                self.x.append(self.geometry[i][2])
                self.y.append(self.geometry[i][3])
                self.z.append(self.geometry[i][4])
                self.no.append(i+1)

    def write_geometry(self, path):
        with open(path, 'a') as f:
            f.write(str(self.number_of_atoms) + '\n')
            for element in self.geometry:
                f.write(str(element[1]).center(11) + ' ')
                f.write('{:.12E}'.format(float(element[2])).rjust(19) + ' ')
                f.write(str(element[3]).rjust(19) + ' ')
                f.write('{:.12E}'.format(float(element[4])).rjust(19))
                f.write('\n')


    def get_layerdistance(self):
        z = [float(i) for i in self.z]
        z_dict = dict(zip(z, self.no))
        z.sort()
        print(z)

        #dlete the repeat atom with the similar z-coordinate
        i = 1
        while i < len(z):
            if abs(z[i] - z[i-1]) < 0.1:
                z.pop(i)
            else:
                i += 1

        #get the longest distance between atom layer
        distance = 0
        z_fixed = [0, 0]
        for i in range(1, len(z)):
            if (abs(z[i] - z[i-1])) > distance:
                distance = abs(z[i] - z[i-1])
                z_fixed[0] = (z[i])
                z_fixed[1] = (z[i-1])
                #print(distance, z_fixed)
        self.layer_distance = distance
        self.z_fixed_no[0] = z_dict[z_fixed[0]]
        self.z_fixed_no[1] = z_dict[z_fixed[1]]
        self.z_fixed_co[0] = self.z[z_dict[z_fixed[0]] - 1]
        self.z_fixed_co[1] = self.z[z_dict[z_fixed[1]] - 1]

        for i in self.no:
            if i not in self.z_fixed_no:
                self.z_free_no.append(i)

        return distance

    def get_fixed_atom_number(self):
        distance = self.get_layerdistance()
        return self.z_fixed_no

    def get_elements(self):
        return self.elements

    def get_geometry(self):
        return self.geometry

    def update(self, key, value):
        self.__dict__[key] = value
        self.__init__(self.init_path, self.geometry)

    def set_fixed_atoms(self, fixed_atoms):
        self.z_fixed_no = [int(i) for i in fixed_atoms]
        self.z_fixed_co = [self.z[int(i)-1] for i in fixed_atoms]
        self.layer_distance = abs(float(self.z_fixed_co[0]) - float(self.z_fixed_co[1]))
        self.z_free_no = [i for i in self.no if i not in self.z_fixed_no]

    def init_geo_from_json(self):
        geometry = []
        for atom in self.json_form:
            line = [atom['nat'], atom['x'], atom['y'], atom['z']]
            geometry.append(line)
        self.geometry = geometry
        for i in range(len(self.geometry)):
            if len(self.geometry[i]) == 4:
                self.geometry[i].insert(0, (i+1))
            self.elements.append(self.geometry[i][1])
            self.x.append(self.geometry[i][2])
            self.y.append(self.geometry[i][3])
            self.z.append(self.geometry[i][4])
            self.no.append(i+1)






# path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\geo_opt\x_-0.150\z_-0.106'
# geo = Geometry(path, fixed_atoms=[4, 6])
# print(geo.layer_distance)




