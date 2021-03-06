#!/usr/bin/python3
import math
import os
import json
import sys
import Cluster
from Cluster.atom import Atom
from Data.Periodict_Table import periodic_table_rev
from Data import read_cov_rad
from Common import Point
from Common import record
from Common import mkdir


class ClusterCutter(object):

    def __init__(
            self,
            job,
            name='cluster',
            factors=[1, 1, 0.7],
            center=[],
            fixed_atoms=[],
            deleted_atoms=[],
            cutting_setting=[],
            geometry_file = ''):

        self.cluster_job = job
        self.cluster_path = job.path
        self.coord = str(job.coord)
        self.name = name
        self.fixed_atoms = fixed_atoms
        self.record_file = self.create_json_file()
        self.geometry_file = geometry_file
        self.dimensionality, self.lattice_vector, self.geometry = self.read_geometry_info()
        self.no, self.nat, self.elements, self.x, self.y, self.z = self.get_xyz()
        self.layer_distance, self.z_fixed = self.get_layer_distance()
        self.upperlayer, self.underlayer = self.get_layers()
        self.original_atoms = self.copy_original_atoms()
        self.atom_coor_dict, self.atoms_coor_vec_dict = self.cal_coordinate_number_of_original_atoms()

        self.central_atoms = center
        self.centre, self.UpperCenter, self.UnderCenter = self.get_centre()
        self.l, self.l1, self.l2, self.l3 = self.get_l()
        self.cutting_factors = factors
        self.deleted_atoms = deleted_atoms
        self.cutting_setting = cutting_setting
        self.record_parameters()

        self.choosed_atoms = []

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def create_json_file(self):
        data = {}
        json_path = self.cluster_job.root_path
        json_file = os.path.join(json_path, 'cluster.json')
        if not os.path.exists(json_file):
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
        return json_file

    def record_data(self, item, value):
        with open(self.record_file, 'r') as f:
            data = json.load(f)
        if self.coord not in data:
            data[self.coord] = {}
        this_data = data[self.coord]
        this_data[item] = value
        with open(self.record_file, 'w') as f:
            json.dump(data, f, indent=4)

    def record_geometry(self, geometry):
        with open(self.record_file, 'r') as f:
            data = json.load(f)
        if self.coord not in data:
            data[self.coord] = {}
        geo_list = []
        for atom in geometry:
            atom_dict = {}
            atom_dict['no'] = atom[0]
            atom_dict['nat'] = atom[1]
            atom_dict['ele'] = atom[2]
            atom_dict['x'] = atom[3]
            atom_dict['y'] = atom[4]
            atom_dict['z'] = atom[5]
            geo_list.append(atom_dict)
        data[self.coord]['geometry'] = geo_list
        with open(self.record_file, 'w') as f:
            json.dump(data, f, indent=4)

    def read_geometry_info(self):
        """
        read dimensionality, lattice vector and geometry infomation from different input
        :return: dimensionality, lattice vector and geometry
        """
        try:
            # try to find infos in CRYSTAL geometry optimization OUTPUT file.
            geo_opt_file = self.cluster_path.replace('cluster', 'geo_opt')
            geo_opt_file = os.path.join(geo_opt_file, 'geo_opt.out')
            dimensionality, lattice_vector, geometry = Cluster.read_info(geo_opt_file)
        except Exception as e:
            print(e)
            try:
                # try to find infos in .ini file
                IniReader = Cluster.GeoIniReader(self.geometry_file)
                dimensionality, lattice_vector, geometry = IniReader.get_infos()
            except Exception as e:
                print(e)
                try:
                    # try to find infos in CRYSTAL INPUT file
                    dimensionality, lattice_vector, geometry = Cluster.read_CrystalInput(self.geometry_file)
                except Exception as e:
                    print(e)
                    print('Please use correct form of geometry input.')
                    print('Programm exits...')
                    sys.exit()
        self.record_data('dimensionality', dimensionality)
        self.record_data('lattice vector', lattice_vector)
        self.record_geometry(geometry)
        return dimensionality, lattice_vector, geometry

    def get_xyz(self):
        """
        split geometry into no. atomic number, element name, and coordinate x, y and z
        :return:
        """
        no = [atom[0] for atom in self.geometry]
        nat = [atom[1] for atom in self.geometry]
        ele = [atom[2] for atom in self.geometry]
        x = [atom[3] for atom in self.geometry]
        y = [atom[4] for atom in self.geometry]
        z = [atom[5] for atom in self.geometry]
        return no, nat, ele, x, y, z

    def get_layer_distance(self):
        """
        calculate the distance between upper- and underlayer, and select the two atoms at the edge of these two layers
        :return:
        """
        z = sorted([float(i) for i in self.z])

        # delete the repeat atom with the similar z-coordinate
        i = 1
        while i < len(z):
            if abs(z[i] - z[i - 1]) < 0.1:
                z.pop(i)
            else:
                i += 1

        # get the longest distance between atom layer
        distance = 0
        z_fixed = [0, 0]
        for i in range(1, len(z)):
            if (abs(z[i] - z[i - 1])) > distance:
                distance = abs(z[i] - z[i - 1])
                z_fixed[0] = (z[i])
                z_fixed[1] = (z[i - 1])

        return distance, z_fixed

    def get_layers(self):
        """
        split the geometry into upper- and underlayer
        :return:
        """
        if self.fixed_atoms is not None and self.fixed_atoms != []:
            fixed_z = [self.z[int(self.fixed_atoms[0]) - 1],
                       self.z[int(self.fixed_atoms[1]) - 1]]
        else:
            fixed_z = self.z_fixed
        upperlayer, underlayer = [], []
        for atom in self.geometry:
            if atom[-1] >= max(fixed_z) - 0.15:
                upperlayer.append(atom)
            else:
                underlayer.append(atom)
        return upperlayer, underlayer

    def get_central_axis_slab(self):
        avg_x = sum(self.x) / len(self.x)
        avg_y = sum(self.y) / len(self.y)
        axis = (avg_x, avg_y)
        upper_x = [atom[3] for atom in self.upperlayer]
        upper_y = [atom[4] for atom in self.upperlayer]
        under_x = [atom[3] for atom in self.underlayer]
        under_y = [atom[4] for atom in self.underlayer]
        avg_x_upper = sum(upper_x) / len(upper_x)
        avg_y_upper = sum(upper_y) / len(upper_y)
        avg_x_under = sum(under_x) / len(under_y)
        avg_y_under = sum(under_y) / len(under_y)
        axis_upper = (avg_x_upper, avg_y_upper)
        axis_under = (avg_x_under, avg_y_under)
        return axis, axis_upper, axis_under

    def get_centre_crystal(self):
        avg_x = sum(self.x) / len(self.x)
        avg_y = sum(self.y) / len(self.y)
        avg_z = sum(self.z) / len(self.z)
        point = (avg_x, avg_y, avg_z)
        upper_x = [atom[3] for atom in self.upperlayer]
        upper_y = [atom[4] for atom in self.upperlayer]
        upper_z = [atom[5] for atom in self.upperlayer]
        under_x = [atom[3] for atom in self.underlayer]
        under_y = [atom[4] for atom in self.underlayer]
        under_z = [atom[5] for atom in self.underlayer]
        avg_x_upper = sum(upper_x) / len(upper_x)
        avg_y_upper = sum(upper_y) / len(upper_y)
        avg_z_upper = sum(upper_z) / len(upper_z)
        avg_x_under = sum(under_x) / len(under_y)
        avg_y_under = sum(under_y) / len(under_y)
        avg_z_under = sum(under_z) / len(under_z)
        point_upper = (avg_x_upper, avg_y_upper, avg_z_upper)
        point_under = (avg_x_under, avg_y_under, avg_z_under)
        return point, point_upper, point_under

    def get_centre(self):
        if self.central_atoms == []:
            if self.dimensionality == 2:
                return self.get_central_axis_slab()
            elif self.dimensionality == 3:
                return self.get_centre_crystal()
        else:
            if len(self.central_atoms) == 2 and isinstance(self.central_atoms[0], list):
                UpperCenter, UnderCenter = self.central_atoms
                atom1, atom2 = UpperCenter
                atom3, atom4 = UnderCenter
                atom1 = self.geometry[int(atom1) - 1]
                atom2 = self.geometry[int(atom2) - 1]
                atom3 = self.geometry[int(atom3) - 1]
                atom4 = self.geometry[int(atom4) - 1]
                avg_x = (atom1[-3] + atom2[-3] + atom3[-3] + atom4[-3]) / 4
                avg_y = (atom1[-2] + atom2[-2] + atom3[-2] + atom4[-2]) / 4
                avg_z = (atom1[-1] + atom2[-1] + atom3[-1] + atom4[-1]) / 4
                upper_avg_x = (atom1[-3] + atom2[-3]) / 2
                upper_avg_y = (atom1[-2] + atom2[-2]) / 2
                upper_avg_z = (atom1[-1] + atom2[-1]) / 2
                under_avg_x = (atom3[-3] + atom4[-3]) / 2
                under_avg_y = (atom3[-2] + atom4[-2]) / 2
                under_avg_z = (atom3[-1] + atom4[-1]) / 2
                if self.dimensionality == 2:
                    center = (avg_x, avg_y)
                    UpperCenter = (upper_avg_x, upper_avg_y)
                    UnderCenter = (under_avg_x, under_avg_y)
                else:
                    center = (avg_x, avg_y, avg_z)
                    UpperCenter = (upper_avg_x, upper_avg_y, upper_avg_z)
                    UnderCenter = (under_avg_x, under_avg_y, under_avg_z)
                return center, UpperCenter, UnderCenter

    def get_l(self):
        """
        get the length of the unit cell
        here l is the diagonal, l1, l2, l3 represents the length of a, b, c of unit cell
        :return:
        """
        l, l1, l2, l3 = 0, 0, 0, 0
        l0 = 0
        vec1, vec2, vec3 = self.lattice_vector
        x1, y1, z1 = vec1
        x2, y2, z2 = vec2
        x3, y3, z3 = vec3
        for i in vec1:
            a = i ** 2
            l1 += a
        for i in vec2:
            a = i ** 2
            l2 += a
        for i in vec3:
            a = i ** 2
            l3 += a
        l1 = math.sqrt(l1)
        l2 = math.sqrt(l2)
        l3 = math.sqrt(l3)
        if self.dimensionality == 2:
            vec = (x2 - x1, y2 - y1, z2 - z1)
            vec0 = (x2 + x1, y2 + y1, z2 + z1)
        else:
            vec = (x1 - x2 - x3, y1 - y2 + y3, z1 - z2 + z3)
            vec0 = (x1 + x2 + x3, y1 + y2 + y3, z1 + z2 + z3)
        for i in vec:
            a = i ** 2
            l += a
        for i in vec0:
            a = i ** 2
            l0 += a
        l = math.sqrt(l)
        l0 = math.sqrt(l0)
        l = max(l, l0)
        return l, l1, l2, l3

    def record_parameters(self):
        try:
            self.record_data('central atoms', self.central_atoms)
            self.record_data('deleted atoms', self.deleted_atoms)
            self.record_data('center', self.centre)
            self.record_data('upper center', self.UpperCenter)
            self.record_data('under center', self.UnderCenter)
            self.record_data('cell size', [self.l, self.l1, self.l2, self.l3])
            self.record_data('cutting factors', self.cutting_factors)
        except Exception as e:
            print(e)

    @staticmethod
    def cal_distance(atom, centre):
        if len(centre) == 2:
            x, y = centre
            dis = math.sqrt(((atom.x - x) ** 2) + ((atom.y - y) ** 2))
        elif len(centre) == 3:
            x, y, z = centre
            dis = math.sqrt(((atom.x - x) ** 2) +
                            ((atom.y - y) ** 2) + ((atom.z - z) ** 2))
        return dis

    @staticmethod
    def cal_vec_distance(atom, centre, vec):
        if len(centre) == 2:
            x, y = centre
            ux = atom.x - x
            uy = atom.y - y
            vx, vy, _ = vec
            proj = (ux * vx + uy * vy) / math.sqrt(vx**2 + vy**2)
        elif len(centre) == 3:
            x, y, z = centre
            ux = atom.x - x
            uy = atom.y - y
            uz = atom.z - z
            vx, vy, vz = vec
            proj = (ux * vx + uy * vy + uz * vz) / \
                math.sqrt(vx**2 + vy**2 + vz**2)
        return abs(proj)

    def copy_original_atoms(self):
        """
        transfer the original atoms in unit cell to Class Atom form
        :return:
        """
        original_atoms = [
            Atom(
                atom[1],
                atom[3],
                atom[4],
                atom[5],
                no=atom[0]) for atom in self.geometry]
        return original_atoms

    @staticmethod
    def generate_new_atom_2d(atom, v1, v2, a1, a2):
        nat = atom.nat
        new_x = atom.x + v1[0] * a1 + v2[0] * a2
        new_y = atom.y + v1[1] * a1 + v2[1] * a2
        new_z = atom.z + v1[2] * a1 + v2[2] * a2
        no = atom.no
        atom_type = atom.type
        coor = atom.coor
        coor_vec = atom.coor_vec
        new_atom = Atom(
            nat,
            new_x,
            new_y,
            new_z,
            no=no,
            type=atom_type,
            coor=coor,
            coor_vec=coor_vec)
        new_atom.layer = atom.layer
        return new_atom

    @staticmethod
    def generate_new_atom_3d(atom, v1, v2, v3, a1, a2, a3):
        nat = atom.nat
        new_x = atom.x + v1[0] * a1 + v2[0] * a2 + v3[0] * a3
        new_y = atom.y + v1[1] * a1 + v2[1] * a2 + v3[0] * a3
        new_z = atom.z + v1[2] * a1 + v2[2] * a2 + v3[0] * a3
        no = atom.no
        atom_type = atom.type
        coor = atom.coor
        coor_vec = atom.coor_vec
        new_atom = Atom(
            nat,
            new_x,
            new_y,
            new_z,
            no=no,
            type=atom_type,
            coor=coor,
            coor_vec=coor_vec)
        new_atom.layer = atom.layer
        return new_atom

    def gen_all_atoms(self, atoms, att):
        """
        generation atoms according to giving vector
        :param atoms:
        :param att:
        :return: new atoms
        """
        new_atoms = []
        v1, v2, v3 = self.lattice_vector
        if len(att) == 2:
            a1, a2 = att
            for i in range(-a1, a1 + 1):
                for j in range(-a2, a2 + 1):
                    for atom in atoms:
                        new_atom = self.generate_new_atom_2d(
                            atom, v1, v2, i, j)
                        if new_atom not in atoms:
                            new_atoms.append(new_atom)
        elif len(att) == 3:
            a1, a2, a3 = att
            for i in range(-a1, a1 + 1):
                for j in range(-a2, a2 + 1):
                    for k in range(-a3, a3 + 1):
                        for atom in atoms:
                            new_atom = self.generate_new_atom_3d(
                                atom, v1, v2, v3, i, j, k)
                            if new_atom not in atoms:
                                new_atoms.append(new_atom)
        return new_atoms

    def choose_atoms_from_distance(self):
        original_atoms = self.original_atoms[:]
        upper_no = [atom[0] for atom in self.upperlayer]
        under_no = [atom[0] for atom in self.underlayer]
        original_upper = [atom for atom in original_atoms if atom.no in upper_no]
        for atom in original_upper:
            atom.layer = 1
        original_under = [atom for atom in original_atoms if atom.no in under_no]
        for atom in original_under:
            atom.layer = 2
        new_atoms = []
        if self.dimensionality == 2:
            ceil = int(math.ceil(max(max(self.cutting_factors[0]), max(self.cutting_factors[1]))))
            vec_att = (ceil, ceil)  # parameter which determines how many times should unit cell be repeated
            curr_upper = self.gen_all_atoms(original_upper, vec_att)
            curr_upper = curr_upper + original_upper[:]
            curr_under = self.gen_all_atoms(original_under, vec_att)
            curr_under += original_under[:]
            fac, fac1, fac2 = self.cutting_factors[0]
            for atom in curr_upper:
                # print(self.cal_distance(atom, self.UpperCenter), self.l*fac)
                # print(self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]), self.l2)
                # print(self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]), self.l1)
                if self.cal_distance(atom, self.UpperCenter) < self.l * fac \
                        and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2 * fac2 \
                        and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1 * fac1:
                    new_atoms.append(atom)
            fac, fac1, fac2 = self.cutting_factors[1]
            for atom in curr_under:
                if self.cal_distance(atom, self.UnderCenter) < self.l * fac \
                        and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2 * fac2 \
                        and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[0]) < self.l1 * fac1:
                    new_atoms.append(atom)
        else:
            fac, fac1, fac2, fac3 = self.cutting_factors[1]
            ceil = int(math.ceil(max(fac1, fac2, fac3)))
            vec_att = (ceil, ceil, ceil)
            curr_upper = self.gen_all_atoms(original_upper, vec_att)
            curr_under = self.gen_all_atoms(original_under, vec_att)
            fac, fac1, fac2, fac3 = self.factors[0]
            for atom in curr_upper:
                if self.cal_distance(atom, self.UpperCenter) < self.l * fac \
                        and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2 * fac2 \
                        and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1 * fac1 \
                        and self.cal_vector_between_two_atoms(atom, self.UpperCenter, self.lattice_vector[2]) < self.l3 * fac3:
                    new_atoms.append(atom)
            fac, fac1, fac2, fac3 = self.factors[1]
            for atom in curr_under:
                if self.cal_distance(atom, self.UnderCenter) < self.l * fac \
                        and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2 * fac2 \
                        and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[0]) < self.l1 * fac1 \
                        and self.cal_vector_between_two_atoms(atom, self.UnderCenter, self.lattice_vector[2]) < self.l3 * fac3:
                    new_atoms.append(atom)

        if original_atoms[0] not in new_atoms:
            choosed_atoms = new_atoms + original_atoms[:]
            # print('number of selected atoms: ', len(choosed_atoms))
            return choosed_atoms
        else:
            # print('number of selected atoms: ', len(new_atoms))
            return new_atoms

    @staticmethod
    def cal_dis_two_atoms(atom1, atom2):
        """
        calculate the distace between two atoms
        :param atom1:
        :param atom2:
        :return: distance
        """
        distance = math.sqrt((atom1.x - atom2.x)**2 +
                             (atom1.y - atom2.y)**2 + (atom1.z - atom2.z)**2)
        return distance

    @staticmethod
    def cal_vector_between_two_atoms(atom1, atom2):
        vector = (atom2.x - atom1.x, atom2.y - atom1.y, atom2.z - atom1.z)
        return (atom2.nat, vector)

    def cal_coordinate_number_of_original_atoms(self):
        """
        according to the distance between two atoms to judge if there is conectivity between these two atoms
        afterwards calculate the coordniation number of each atom
        and calculate the direction of each coordinated atom of each atom
        :return:
        """
        if self.dimensionality == 2:
            vec = (1, 1)
        else:
            vec = (1, 1, 1)
        new_atoms = self.gen_all_atoms(self.original_atoms, vec)
        all_atoms = new_atoms + self.original_atoms
        for i in range(len(self.original_atoms)):
            coor = 0
            coor_vec = []
            for new_atom in all_atoms:
                if new_atom != self.original_atoms[i]:
                    cov_rad = (
                        read_cov_rad(
                            self.original_atoms[i].nat,
                            unit='a') + read_cov_rad(
                            new_atom.nat,
                            unit='a')) * 1.1
                    distance = self.cal_dis_two_atoms(
                        self.original_atoms[i], new_atom)
                    if distance <= cov_rad:
                        #print(self.original_atoms[i], new_atom.nat, distance, cov_rad)
                        vec = self.cal_vector_between_two_atoms(
                            self.original_atoms[i], new_atom)
                        coor_vec.append(vec)
                        coor += 1
            self.original_atoms[i].coor = coor
            # print(coor)
            self.original_atoms[i].coor_vec = coor_vec
            # print(coor_vec)
        atoms_coor_dict, atoms_coor_vec_dict = {}, {}
        for atom in self.original_atoms:
            atoms_coor_dict[atom.no] = atom.coor
            atoms_coor_vec_dict[atom.no] = atom.coor_vec
        return atoms_coor_dict, atoms_coor_vec_dict

    def cal_coor_no_of_all_atoms(self, atoms):
        for i in range(len(atoms)):
            coor = 0
            coor_vec = []
            for j in range(len(atoms)):
                if i != j:
                    cor_rad = read_cov_rad(
                        atoms[i].nat, unit='a') + read_cov_rad(atoms[j].nat, unit='a')
                    dis = self.cal_dis_two_atoms(atoms[i], atoms[j])
                    if dis <= cor_rad * 1.1 and dis > 0:
                        # print(atoms[i], atoms[j], cor_rad*1.2, dis)
                        vec = self.cal_vector_between_two_atoms(
                            atoms[i], atoms[j])
                        coor_vec.append(vec)
                        coor += 1
            atoms[i].coor = coor
            atoms[i].coor_vec = coor_vec
        # for i in self.original_atoms:
        #     print(i.coor)
        return atoms

    def select_atoms_according_coordinate(self, atoms):
        while True:
            new_atoms = []
            for atom in atoms:
                if self.atom_coor_dict[atom.no] >= 3:
                    if atom.coor >= self.atom_coor_dict[atom.no] - 1:
                        new_atoms.append(atom)
                else:
                    if atom.coor == self.atom_coor_dict[atom.no]:
                        new_atoms.append(atom)
            if len(new_atoms) == len(atoms):
                break
            atoms = self.cal_coor_no_of_all_atoms(new_atoms)
        return new_atoms

    def get_free_coor_vector(self):
        for atom in self.choosed_atoms:
            coor_vec = atom.coor_vec
            coor_vec_original = self.atoms_coor_vec_dict[atom.no]
            new_coor_vec = [
                vec for vec in coor_vec_original if vec not in coor_vec]
            new_vecs = []
            for vec in new_coor_vec:
                para_list = [self.if_parallel(vec, vec2) for vec2 in coor_vec]
                if not any(para_list):
                    new_vecs.append(vec)
            atom.coor_vec_free = new_vecs

    @staticmethod
    def if_parallel(vec1, vec2):
        # print('1:', vec1, '2:', vec2)
        nat1, vec1 = vec1
        x1, y1, z1 = vec1
        nat2, vec2 = vec2
        x2, y2, z2 = vec2
        a = x1 / x2
        b = y1 / y2
        c = z1 / z2
        # try:
        #     a = x1/x2
        # except ZeroDivisionError:
        #     a = 0
        # try:
        #     b = y1/y2
        # except ZeroDivisionError:
        #     b = 0
        # try:
        #     c = z1/z2
        # except ZeroDivisionError:
        #     c = 0
        if abs(a - b) + abs(a - c) + abs(b - c) < 0.0001:
            return True
        else:
            return False

    @staticmethod
    def get_new_atom_according_to_vetor(c_atom, vec, length, nat):
        c = Point(c_atom.x, c_atom.y, c_atom.z)
        _, vec = vec
        vec_x, vec_y, vec_z = vec
        vec_point = Point(vec_x, vec_y, vec_z)
        vec_len = vec_point.length()
        s = length / vec_len
        new_vec = vec_point * s
        new_point = c + new_vec
        new_atom = Atom(nat, new_point.x, new_point.y, new_point.z, coor=1)
        return new_atom

    def add_H(self):
        self.get_free_coor_vector()
        new_Hs = []
        for atom in self.choosed_atoms:
            if len(atom.coor_vec_free) > 0:
                length = read_cov_rad(atom.nat, unit='a') + \
                    read_cov_rad('1', unit='a')
                new_H = self.get_new_atom_according_to_vetor(
                    atom, atom.coor_vec_free[0], length, nat='1')
                new_Hs.append(new_H)
        final_cluster = self.choosed_atoms + new_Hs
        return final_cluster

    def delete_atoms(self, choosed_atoms):
        if len(self.deleted_atoms) == 0:
            return choosed_atoms
        else:
            deleted_atoms = [i - 1 for i in self.deleted_atoms]
            choosed_atoms = [i for j, i in enumerate(
                choosed_atoms) if j not in deleted_atoms]
            choosed_atoms = self.cal_coor_no_of_all_atoms(choosed_atoms)
            choosed_atoms = self.select_atoms_according_coordinate(
                choosed_atoms)
            return choosed_atoms

    def get_cluster(self):
        coord, add_h = self.cutting_setting
        self.choosed_atoms = self.choose_atoms_from_distance()
        self.choosed_atoms = self.cal_coor_no_of_all_atoms(self.choosed_atoms)
        if coord is True:
            self.choosed_atoms = self.select_atoms_according_coordinate(self.choosed_atoms)
        self.choosed_atoms = self.delete_atoms(self.choosed_atoms)
        if add_h is True:
            self.choosed_atoms = self.add_H()
        self.choosed_atoms = self.add_layer_number(self.choosed_atoms)
        self.record_cluster()

    def record_cluster(self):
        with open(self.record_file, 'r') as f:
            data = json.load(f)
        geo_list = []
        for atom in self.choosed_atoms:
            atom_dict = {}
            atom_dict['no'] = atom.no
            atom_dict['nat'] = atom.nat
            atom_dict['ele'] = atom.element
            atom_dict['x'] = atom.x
            atom_dict['y'] = atom.y
            atom_dict['z'] = atom.z
            atom_dict['coordinate number'] = atom.coor
            atom_dict['coordinate vector'] = atom.coor_vec
            atom_dict['layer'] = atom.layer
            atom_dict['type'] = atom.type
            geo_list.append(atom_dict)
        data[str(self.cluster_job.coord)]['cluster'] = geo_list
        with open(self.record_file, 'w') as f:
            json.dump(data, f, indent=4)

    def write_xyz(self, cluster=[]):
        """
        wriete the cutted cluster into a .xyz format file
        :return:
        """
        if len(self.choosed_atoms) == 0:
            self.get_cluster()
        if len(cluster) == 0:
            cluster = self.choosed_atoms
        file_name = '{}_Cluster.xyz'.format(self.name)
        file_path = os.path.join(self.cluster_path, file_name)
        with open(file_path, 'w') as f:
            f.write(str(len(cluster)) + '\n')
            f.write('{}_Cluster'.format(self.name) + '\n')
            for atom in cluster:
                ele = periodic_table_rev[int(atom.nat)]
                f.write(str(ele).center(6) + ' ')
                f.write('{:.12E}'.format(float(atom.x)).rjust(19) + ' ')
                f.write('{:.12E}'.format(float(atom.y)).rjust(19) + ' ')
                f.write('{:.12E}'.format(float(atom.z)).rjust(19))
                f.write('\n')
            print('Geometry file generated.')
            print('number of atoms: ', len(cluster))
            print('---' * 15)

    def add_layer_number(self, cluster):
        for atom in cluster:
            if atom.z >= max(self.z_fixed) - 0.1 * self.layer_distance:
                atom.layer = 1
            else:
                atom.layer = 2
        return cluster

    def write_xyz_with_layernumber(self, cluster=[]):
        if len(self.choosed_atoms) == 0:
            self.get_cluster()
        if len(cluster) == 0:
            cluster = self.choosed_atoms
        file_name = '{}_Cluster.xyz'.format(self.name)
        file_path = os.path.join(self.cluster_path, file_name)
        if not os.path.exists(self.cluster_path):
            mkdir(self.cluster_path)
        with open(file_path, 'w') as f:
            f.write(str(len(cluster)) + '\n')
            f.write('{}_Cluster'.format(self.name) + '\n')
            for atom in cluster:
                ele = periodic_table_rev[int(atom.nat)]
                f.write((str(ele) + str(atom.layer)).center(6) + ' ')
                f.write('{:.12E}'.format(float(atom.x)).rjust(19) + ' ')
                f.write('{:.12E}'.format(float(atom.y)).rjust(19) + ' ')
                f.write('{:.12E}'.format(float(atom.z)).rjust(19))
                f.write('\n')
            rec = str(self.cluster_job) + '\n'
            rec += 'Geometry file generated.\n'
            rec += 'Number of atoms in cluster: {}\n'.format(len(cluster))
            rec += '---' * 25
            print(rec)
            record(self.cluster_job.root_path, rec)
