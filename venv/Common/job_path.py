#!/usr/bin/python3
import os

class Job_path(object):

    def __init__(self, path, init_dist = 0):
        self.path = path
        self.z = ''
        self.x = ''
        self.z_dirname = ''
        self.x_dirname = ''
        self.layertype = 'bilayer'
        self.method_name = ''
        self.method = ''
        self.root_path = ''
        self.init_dist = init_dist

        self.init_values()
        self.coord = (self.x, self.z)

        self.parameter = {}
        self.status = ''

    def __str__(self):
        return self.method + ' (x: {}, z: {}) '.format(self.x, self.z) + self.layertype

    def __repr__(self):
        return self.method + ' (x: {}, z: {}) '.format(self.x, self.z) + self.layertype


    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __cmp__(self, other):
        if float(self.x) < float(other.x):
            return -1
        elif float(self.x) == float(other.x):
            if float(self.z) < float(other.z):
                return -1
            elif float(self.z) == float(other.z):
                return 0
            else:
                return 1
        else:
            return 1

    def __eq__(self, other):
        if self.path == other.path and self.layertype == other.layertype and self.method == other.method:
            return True
        return False

    def __hash__(self):
        return hash(id(self))

    def init_values(self):
        z = os.path.split(self.path)[-1]
        path = os.path.split(self.path)[0]
        if z == 'underlayer' or z =='upperlayer':
            self.layertype = z
            z = os.path.split(path)[-1]
            path  = os.path.split(path)[0]
        self.z_dirname = z
        z = z.split('_')[-1]
        self.z = z

        x = os.path.split(path)[-1]
        path = os.path.split(path)[0]
        self.x_dirname = x
        x = x.split('_')[-1]
        self.x = x

        method = os.path.split(path)[-1]
        self.method_name = self.method_name_transfer(method)
        self.method = method
        self.root_path = os.path.split(path)[0]

    @staticmethod
    def method_name_transfer(method):
        method_dict = {'hf_2': 'HF2', 'hf2': 'HF2', 'hf_1': 'HF1', 'hf1': 'HF1', 'geo_opt': 'Geometry Optimization', 'lmp2': 'LMP2', 'rpa': 'LRPA', 'lrpa': 'LRPA', 'cluster': 'Cluster'}
        method = method.lower()
        if method in method_dict:
            method = method_dict[method]
        else:
            print('method not in method dict.')
            method = method.upper()
        return method

    def get_z_value(self):
        try:
            z = float(self.z)
        except Exception as e:
            print(e)
        finally:
            return z

    def get_x_value(self):
        try:
            x = float(self.x)
        except Exception as e:
            print(e)
        finally:
            return x

    def get_absolut_distance(self):
        if self.init_dist == 0:
            print('There is no initial distance!!!\n'
                  'Plese initilize the job path instance with an initial distance.')
        try:
            z = self.get_z_value()
            abs_dist = self.init_dist + z
            return abs_dist
        except Exception as e:
            print(e)

    def reset(self, key, value):
        """
        rebuild the object by changing one attribue
        key could be method, layertype, x_dirname or z_dirname
        :param key:
        :param value:
        :return:
        """
        old = self.__dict__[key]
        path = self.path.replace(old, value)
        self.__init__(path)

    def set_status(self, stauts):
        stauts_list = ['', 'prepared', 'submitted', 'calculated', 'finished', 'not converged', 'error']
        if stauts.lower() in stauts_list:
            self.status = stauts
        else:
            print('wrong job status')

# path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_2\x_-0.150\z_-0.106'
# job = Job_path(path)
# job.reset('method', 'lmp2')
# print(job)
# print(job)
# job2 = copy.deepcopy(job)
# job2.reset('method', 'hf_1')
# print(job)
# print(job2)


