#!/usr/bin/python3
import math
import os
from Common import Job_path
from Common import mkdir
from CLUSTER.read_info import read_and_write_infos
from CLUSTER.atom import Atom
from Data.Periodict_Table import periodic_table_rev
from Data import read_cov_rad
from Common import Point



class Cluster(object):

    def __init__(self, job, centre = [], name = '', fixed_atoms=None, size='', factors=[], zoom=1, aspect_ratio=0, basic_infos=[]):

        self.job = job
        self.name = name
        self.fixed_atoms = fixed_atoms
        self.centre_manu = centre
        self.UpperCenter_manu, self.UnderCenter_manu = self.read_Center()
        self.size = size.upper()
        self.cluster_job, self.cluster_path = self.get_new_job()

        self.basic_infos = basic_infos
        self.dimensionality, self.lattice_vector, self.geometry = self.get_infos()
        self.no, self.nat, self.elements, self.x, self.y, self.z = self.get_xyz()
        self.layer_distance, self.z_fixed = self.get_layer_distance()
        self.upperlayer, self.underlayer = self.get_layers()
        self.original_atoms = self.get_original_atoms()
        self.atom_coor_dict, self.atoms_coor_vec_dict = self.cal_coordinate_number_of_original_atoms()

        self.factors = factors
        self.zoom = zoom
        self.aspect_ratio = aspect_ratio
        self.fac1, self.fac2 = self.get_aspect_ratio_factor()
        self.centre, self.UpperCenter, self.UnderCenter = self.get_centre()
        self.centre, self.UpperCenter, self.UnderCenter = self.get_center_ma()
        self.l, self.l1, self.l2, self.l3 = self.get_l()

        self.choosed_atoms = []
        self.final_cluster = []


    def __setitem__(self, key, value):
        self._item[index] = value


    def get_new_job(self):
        old_path = self.job.path
        new_path = old_path.replace('geo_opt', 'cluster')
        new_job = Job_path(new_path)
        return new_job, new_path


    def read_Center(self):
        UpperCenter, UnderCenter = None, None
        if type(self.centre_manu) == list and len(self.centre_manu) != 0:
            if type(self.centre_manu[0]) == list and len(self.centre_manu) == 2:
                UpperCenter, UnderCenter = self.centre_manu
        return UpperCenter, UnderCenter


    def get_infos(self):
        """
        get dimensionality, lattice vector and geometry from Geo Opt output file or CRYSTAL INPUT file
        :return: dimensionality, lattice vector and geometry
        """
        if len(self.basic_infos) != 0:
            try:
                dimensionality, lattice_vector, geometry =self.basic_infos
            except Exception as e:
                pass
        else:
            dimensionality, lattice_vector, geometry = read_and_write_infos(self.job)
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
        z = [float(i) for i in self.z]
        z.sort()

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

        return distance, z_fixed


    def get_layers(self):
        """
        split the geometry into upper- and underlayer
        :return:
        """
        if self.fixed_atoms != None:
            fixed_z = [self.z[int(self.fixed_atoms[0])], self.z[int(self.fixed_atoms[1])]]
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
        avg_x = sum(self.x)/len(self.x)
        avg_y = sum(self.y)/len(self.y)
        axis = (avg_x, avg_y)
        upper_x = [atom [3] for atom in self.upperlayer]
        upper_y = [atom [4] for atom in self.upperlayer]
        under_x = [atom [3] for atom in self.underlayer]
        under_y = [atom [4] for atom in self.underlayer]
        avg_x_upper = sum(upper_x)/len(upper_x)
        avg_y_upper = sum(upper_y)/len(upper_y)
        avg_x_under = sum(under_x)/len(under_y)
        avg_y_under = sum(under_y)/len(under_y)
        axis_upper = (avg_x_upper, avg_y_upper)
        axis_under = (avg_x_under, avg_y_under)
        return axis, axis_upper, axis_under


    def get_centre_crystal(self):
        avg_x = sum(self.x)/len(self.x)
        avg_y = sum(self.y)/len(self.y)
        avg_z = sum(self.z)/len(self.z)
        point = (avg_x, avg_y,avg_z)
        upper_x = [atom [3] for atom in self.upperlayer]
        upper_y = [atom [4] for atom in self.upperlayer]
        upper_z = [atom [5] for atom in self.upperlayer]
        under_x = [atom [3] for atom in self.underlayer]
        under_y = [atom [4] for atom in self.underlayer]
        under_z = [atom [5] for atom in self.underlayer]
        avg_x_upper = sum(upper_x)/len(upper_x)
        avg_y_upper = sum(upper_y)/len(upper_y)
        avg_z_upper = sum(upper_z)/len(upper_z)
        avg_x_under = sum(under_x)/len(under_y)
        avg_y_under = sum(under_y)/len(under_y)
        avg_z_under = sum(under_z)/len(under_z)
        point_upper = (avg_x_upper, avg_y_upper, avg_z_upper)
        point_under = (avg_x_under, avg_y_under, avg_z_under)
        return point, point_upper, point_under


    def get_centre(self):
        if self.dimensionality == 2:
            return self.get_central_axis_slab()
        elif self.dimensionality == 3:
            return self.get_centre_crystal()


    def get_center_ma(self):
        """
        get the center of the system by manually entering the central atoms, and use the central point of these two atoms
        :return: center(x, y, (z))
        """
        if len(self.centre_manu) == 2:
            if self.UnderCenter_manu == None:
                atom1 = self.geometry[self.centre_manu[0]-1]
                atom2 = self.geometry[self.centre_manu[1]-1]
                avg_x = (atom1[-3]+atom2[-3])/2
                avg_y = (atom1[-2]+atom2[-2])/2
                avg_z = (atom1[-1]+atom2[-1])/2
                if self.dimensionality == 2:
                    center = (avg_x, avg_y)
                    UpperCenter = center
                    UnderCenter = center
                else:
                    center = (avg_x, avg_y, avg_z)
                    UpperCenter = center
                    UnderCenter = center
            else:
                atom1 = self.geometry[self.UpperCenter_manu[0]-1]
                atom2 = self.geometry[self.UpperCenter_manu[1]-1]
                atom3 = self.geometry[self.UnderCenter_manu[0]-1]
                atom4 = self.geometry[self.UnderCenter_manu[1]-1]
                avg_x = (atom1[-3] + atom2[-3] + atom3[-3] + atom4[-3])/4
                avg_y = (atom1[-2] + atom2[-2] + atom3[-2] + atom4[-2])/4
                avg_z = (atom1[-1] + atom2[-1] + atom3[-1] + atom4[-1])/4
                upper_avg_x = (atom1[-3]+atom2[-3])/2
                upper_avg_y = (atom1[-2]+atom2[-2])/2
                upper_avg_z = (atom1[-1]+atom2[-1])/2
                under_avg_x = (atom3[-3]+atom4[-3])/2
                under_avg_y = (atom3[-2]+atom4[-2])/2
                under_avg_z = (atom3[-1]+atom4[-1])/2
                if self.dimensionality == 2:
                    center = (avg_x, avg_y)
                    UpperCenter = (upper_avg_x, upper_avg_y)
                    UnderCenter = (under_avg_x, under_avg_y)
                    #print(center, UpperCenter, UnderCenter)
                else:
                    center = (avg_x, avg_y, avg_z)
                    UpperCenter = (upper_avg_x, under_avg_y, under_avg_z)
                    UnderCenter = (under_avg_x, under_avg_y, under_avg_z)
            return  center, UpperCenter, UnderCenter

        else:
            return self.centre, self.UpperCenter, self.UnderCenter


    @staticmethod
    def cal_distance(atom, centre):
        if len(centre) == 2:
            x, y = centre
            dis = math.sqrt(((atom.x - x) ** 2) + ((atom.y - y) ** 2))
        elif len(centre) == 3:
            x, y, z = centre
            dis = math.sqrt(((atom.x - x) ** 2) + ((atom.y - y) ** 2) + ((atom.z - z) ** 2))
        return dis

    @staticmethod
    def cal_vec_distance(atom,centre,vec):
        if len(centre) == 2:
            x, y = centre
            ux = atom.x - x
            uy = atom.y - y
            u = (ux, uy)
            vx, vy, _ = vec
            proj = (ux*vx + uy*vy) / math.sqrt(vx**2 + vy**2)
        elif len(centre) == 3:
            x, y, z =centre
            ux = atom.x - x
            uy = atom.y - y
            uz = atom.z - z
            u = (ux, uy, uz)
            vx, vy, vz = vec
            proj = (ux*vx + uy*vy + uz*vz) / math.sqrt(vx**2 + vy**2 + yz**2)
        return abs(proj)

    @staticmethod
    def generate_new_atom_2d(atom, v1, v2, a1, a2):
        nat = atom.nat
        new_x = atom.x + v1[0]*a1 + v2[0]*a2
        new_y = atom.y + v1[1]*a1 + v2[1]*a2
        new_z = atom.z + v1[2]*a1 + v2[2]*a2
        no = atom.no
        type = atom.type
        coor = atom.coor
        coor_vec = atom.coor_vec
        new_atom = Atom(nat, new_x, new_y, new_z, no=no, type=type, coor=coor, coor_vec=coor_vec)
        return new_atom


    @staticmethod
    def generate_new_atom_3d(atom, v1, v2, v3, a1, a2, a3):
        nat = atom.nat
        new_x = atom.x + v1[0]*a1 + v2[0]*a2 + v3[0]*a3
        new_y = atom.y + v1[1]*a1 + v2[1]*a2 + v3[0]*a3
        new_z = atom.z + v1[2]*a1 + v2[2]*a2 + v3[0]*a3
        no = atom.no
        type = atom.type
        coor = atom.coor
        coor_vec = atom.coor_vec
        new_atom = Atom(nat, new_x, new_y, new_z, no=no, type=type, coor=coor, coor_vec=coor_vec)
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
            for i in range(-a1, a1+1):
                for j in range(-a2, a2+1):
                    for atom in atoms:
                        new_atom = self.generate_new_atom_2d(atom, v1, v2, i, j)
                        if new_atom not in atoms:
                            new_atoms.append(new_atom)
        elif len(att) == 3:
            a1, a2, a3 = att
            for i in range(-a1, a1+1):
                for j in range(-a2, a2+1):
                    for k in range(-a3, a3+1):
                        for atom in atoms:
                            new_atom = self.generate_new_atom_3d(atom, v1, v2, v3, i, j, k)
                            if new_atom not in atoms:
                                new_atoms.append(new_atom)
        return new_atoms


    def get_l(self):
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
            vec = (x2-x1, y2-y1, z2-z1)
            vec0 = (x2+x1, y2+y1, z2+z1)
        else:
            vec = (x1-x2-x3, y1-y2+y3, z1-z2+z3)
            vec0 = (x1+x2+x3, y1+y2+y3, z1+z2+z3)
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


    def get_original_atoms(self):
        original_atoms = [Atom(atom[1], atom[3], atom[4], atom[5], no=atom[0]) for atom in self.geometry]
        return original_atoms


    def get_aspect_ratio_factor(self):
        if self.aspect_ratio == 0:
            fac1, fac2 = 1, 1
        elif self.aspect_ratio == 1:
            fac1 = 0.85
            fac2 = 1.21
        else:
            n = 0.7 *self.aspect_ratio
            i = (n-1)/(n+1)
            fac1 = 1 - i
            fac2 = 1 + i
        return fac1, fac2



    def choose_atoms_from_distance(self):
        original_atoms = self.original_atoms
        upper_no = [atom[0] for atom in self.upperlayer]
        under_no = [atom[0] for atom in self.underlayer]
        original_upper = [atom for atom in original_atoms if atom.no in upper_no]
        original_under = [atom for atom in original_atoms if atom.no in under_no]
        if self.check_factors():
            new_atoms = self.select_atoms_according_to_factors(original_upper, original_under)
        else:
            new_atoms, new_upper, new_under = [], [], []
            if self.dimensionality == 2:
                if self.size == 'XS':
                    vec_att = (1, 1)
                    curr_atoms = self.gen_all_atoms(original_atoms, vec_att)
                    curr_upper = self.gen_all_atoms(original_upper, vec_att)
                    curr_under = self.gen_all_atoms(original_under, vec_att)
                    for atom in curr_upper:
                        if self.cal_distance(atom, self.UpperCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2 and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1*self.zoom*self.fac1:
                            new_atoms.append(atom)
                    for atom in curr_under:
                        if self.cal_distance(atom, self.UnderCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2 and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[0]) < self.l1*self.zoom*self.fac1:
                            new_atoms.append(atom)
                elif self.size == 'S':
                    vec_att = (1, 1)
                    curr_upper = self.gen_all_atoms(original_upper, vec_att)
                    curr_under = self.gen_all_atoms(original_under, vec_att)
                    for atom in curr_upper:
                        if self.cal_distance(atom, self.UpperCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2 and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1*self.zoom*self.fac1:
                            new_atoms.append(atom)
                    for atom in curr_under:
                        if self.cal_distance(atom, self.UnderCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2:
                            new_atoms.append(atom)
                elif self.size == 'M':
                    vec_att = (1, 1)
                    curr_atoms = self.gen_all_atoms(original_atoms, vec_att)
                    curr_upper = self.gen_all_atoms(original_upper, vec_att)
                    curr_under = self.gen_all_atoms(original_under, vec_att)
                    for atom in curr_upper:
                        if self.cal_distance(atom, self.UpperCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2:
                            new_atoms.append(atom)
                    for atom in curr_under:
                        if self.cal_distance(atom, self.UnderCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2:
                            new_atoms.append(atom)
                elif self.size == 'L':
                    vec_att = (2, 2)
                    curr_upper = self.gen_all_atoms(original_upper, vec_att)
                    curr_under = self.gen_all_atoms(original_under, vec_att)
                    for atom in curr_upper:
                        if self.cal_distance(atom, self.UpperCenter) < self.l*1.2*self.zoom and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*1.3*self.zoom*self.fac2 and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1*1.8*self.zoom*self.fac1:
                            # print(self.cal_distance(atom, self.centre), self.l)
                            # print(self.cal_vec_distance(atom, self.centre, self.lattice_vector[1]), self.l2)
                            # print(self.cal_vec_distance(atom, self.centre, self.lattice_vector[0]), self.l1)
                            new_atoms.append(atom)
                    for atom in curr_under:
                        if self.cal_distance(atom, self.UnderCenter) < self.l*self.zoom and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*0.7*self.zoom*self.fac2:
                            new_atoms.append(atom)
                elif self.size == 'XL':
                    vec_att = (2, 2)
                    curr_atoms = self.gen_all_atoms(original_atoms, vec_att)
                    curr_upper = self.gen_all_atoms(original_upper, vec_att)
                    curr_under = self.gen_all_atoms(original_under, vec_att)
                    for atom in curr_upper:
                        if self.cal_distance(atom, self.UpperCenter) < self.l*1.2*self.zoom and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*1.3*self.zoom*self.fac2 and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1*1.8*self.zoom*self.fac1:
                            new_atoms.append(atom)
                    for atom in curr_under:
                        if self.cal_distance(atom, self.UnderCenter) < self.l*1.2*self.zoom and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*1.3*self.zoom*self.fac2 and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[0]) < self.l1*1.8*self.zoom*self.fac1:
                            new_atoms.append(atom)
            else:
                pass
        choosed_atoms = new_atoms + original_atoms
        choosed_atoms = self.cal_coor_no_of_all_atoms(choosed_atoms)
        choosed_atoms = self.select_atoms_according_coordinate(choosed_atoms)
        # print('number of selected atoms: ', len(choosed_atoms))
        return choosed_atoms


    def select_atoms_according_to_factors(self, original_upper, original_under):
        fac, fac1, fac2, fac3 = self.factors
        new_atoms = []
        if self.dimensionality == 2:
            ceil = int(math.ceil(max(fac1, fac2)))
            vec_att = (ceil, ceil)
            curr_upper = self.gen_all_atoms(original_upper, vec_att)
            curr_under = self.gen_all_atoms(original_under, vec_att)
            for atom in curr_upper:
                if self.cal_distance(atom, self.UpperCenter) < self.l*fac and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*fac2 and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1*fac1:
                    new_atoms.append(atom)
            for atom in curr_under:
                if self.cal_distance(atom, self.UnderCenter) < self.l*fac and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*fac2 and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[0]) < self.l1*fac1:
                    new_atoms.append(atom)
        else:
            ceil = int(math.ceil(max(fac1, fac2, fac3)))
            vec_att = (ceil, ceil, ceil)
            curr_upper = self.gen_all_atoms(original_upper, vec_att)
            curr_under = self.gen_all_atoms(original_under, vec_att)
            for atom in curr_upper:
                if self.cal_distance(atom, self.UpperCenter) < self.l*fac and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[1]) < self.l2*fac2 and self.cal_vec_distance(atom, self.UpperCenter, self.lattice_vector[0]) < self.l1*fac1 and self.cal_vector_between_two_atoms(atom, self.UpperCenter, self.lattice_vector[2]) < self.l3*fac3:
                    new_atoms.append(atom)
            for atom in curr_under:
                if self.cal_distance(atom, self.UnderCenter) < self.l*fac and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[1]) < self.l2*fac2 and self.cal_vec_distance(atom, self.UnderCenter, self.lattice_vector[0]) < self.l1*fac1 and self.cal_vector_between_two_atoms(atom, self.UnderCenter, self.lattice_vector[2]) < self.l3*fac3:
                    new_atoms.append(atom)

        return new_atoms



    def check_factors(self):
        fac, fac1, fac2, fac3 = self.factors
        if self.dimensionality == 2:
            if self.check_factor(fac) and self.check_factor(fac1) and self.check_factor(fac2):
                return True
        elif self.dimensionality == 3:
            if self.check_factor(fac) and self.check_factor(fac1) and self.check_factor(fac2) and self.check_factor(fac3):
                return True
        return False


    def check_factor(self, fac):
        try:
            fac = float(fac)
            if fac > 0:
                return True
            else:
                return False
        except:
            return False


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
                    cov_rad = (read_cov_rad(self.original_atoms[i].nat, unit='a') + read_cov_rad(new_atom.nat, unit='a')) * 1.2
                    distance = self.cal_dis_two_atoms(self.original_atoms[i], new_atom)
                    if distance <= cov_rad:
                        vec = self.cal_vector_between_two_atoms(self.original_atoms[i], new_atom)
                        coor_vec.append(vec)
                        coor +=1
            self.original_atoms[i].coor = coor
            self.original_atoms[i].coor_vec = coor_vec
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
                    cor_rad = read_cov_rad(atoms[i].nat, unit='a') + read_cov_rad(atoms[j].nat, unit='a')
                    dis = self.cal_dis_two_atoms(atoms[i], atoms[j])
                    if dis <= cor_rad*1.2:
                        vec = self.cal_vector_between_two_atoms(atoms[i], atoms[j])
                        coor_vec.append(vec)
                        coor +=1
            atoms[i].coor = coor
            atoms[i].coor_vec = coor_vec
        return atoms


    @staticmethod
    def cal_vector_between_two_atoms(atom1, atom2):
        vector = (atom2.x-atom1.x, atom2.y-atom1.y, atom2.z-atom1.z)
        return (atom2.nat, vector)


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
                # if atom.coor > self.atom_coor_dict[atom.no] - 2 and atom.coor > 0:
                    # if atom.coor != self.atom_coor_dict[atom.no] and self.atom_coor_dict[atom.no] > 2:
                    #     new_atoms.append(atom)
                    # elif atom.coor == self.atom_coor_dict[atom.no]:
                    #     new_atoms.append(atom)
                    # new_atoms.append(atom)
            if len(new_atoms) == len(atoms):
                break
            atoms = self.cal_coor_no_of_all_atoms(new_atoms)
        return new_atoms


    @staticmethod
    def cal_dis_two_atoms(atom1, atom2):
        """
        calculate the distace between two atoms
        :param atom1:
        :param atom2:
        :return: distance
        """
        distance = math.sqrt((atom1.x-atom2.x)**2 + (atom1.y-atom2.y)**2 + (atom1.z-atom2.z)**2)
        return distance


    def add_H(self):
        self.get_free_coor_vector()
        new_Hs = []
        for atom in self.choosed_atoms:
            if len(atom.coor_vec_free) > 0:
                length = read_cov_rad(atom.nat, unit='a') + read_cov_rad('1', unit='a')
                new_H = self.get_new_atom_according_to_vetor(atom, atom.coor_vec_free[0], length, nat='1')
                new_Hs.append(new_H)
        final_cluster = self.choosed_atoms + new_Hs
        return final_cluster


    def get_free_coor_vector(self):
        for atom in self.choosed_atoms:
            coor_vec = atom.coor_vec
            coor_vec_original = self.atoms_coor_vec_dict[atom.no]
            new_coor_vec = [vec for vec in coor_vec_original if vec not in coor_vec]
            new_vecs = []
            for vec in new_coor_vec:
                para_list = [self.if_parallel(vec, vec2) for vec2 in coor_vec]
                if not any(para_list):
                    new_vecs.append(vec)
            atom.coor_vec_free = new_vecs


    def get_new_atom_according_to_vetor(self, c_atom, vec, length, nat):
        c = Point(c_atom.x, c_atom.y, c_atom.z)
        _, vec = vec
        vec_x, vec_y, vec_z = vec
        vec_point = Point(vec_x, vec_y, vec_z)
        vec_len = vec_point.length()
        s = length/vec_len
        new_vec = vec_point * s
        new_point = c + new_vec
        new_atom = Atom(nat, new_point.x, new_point.y, new_point.z, coor=1)
        return new_atom


    @staticmethod
    def if_parallel(vec1, vec2):
        nat1, vec1 = vec1
        x1, y1, z1 = vec1
        nat2, vec2 = vec2
        x2, y2, z2 = vec2
        a = x1/x2
        b = y1/y2
        c = z1/z2
        if abs(a-b) + abs(a-c) + abs(b-c) < 0.0001:
            return True
        else:
            return False


    def get_cluster(self):
        self.choosed_atoms = self.choose_atoms_from_distance()
        self.final_cluster = self.add_H()


    def write_xyz(self, cluster=[]):
        """
        wriete the cutted cluster into a .xyz format file
        :return:
        """
        if self.final_cluster == []:
            self.get_cluster()
        if cluster == []:
            cluster = self.final_cluster
        file_name = '{}_Cluster_{}.xyz'.format(self.name, self.size)
        mkdir(self.cluster_path)
        file_path = os.path.join(self.cluster_path, file_name)
        with open(file_path, 'w') as f:
            f.write(str(len(cluster)) + '\n')
            if self.size != '':
                f.write('{}_Cluster_{}'.format(self.name, self.size) + '\n')
            else:
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
            print('---'*15)



