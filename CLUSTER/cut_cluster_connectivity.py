#!/usr/bin/python3
import math
import os
from CLUSTER import Cluster
from Common import Job_path
from Common import mkdir
from CLUSTER.read_info import read_and_write_infos
from CLUSTER.atom import Atom
from Data.Periodict_Table import periodic_table_rev
from Data import read_cov_rad
from Common import Point



class ClusterConec(Cluster):

    def __init__(self, job, centre = [], name = '', fixed_atoms=None, size='S', basic_infos=[], zoom=1):
        super().__init__(job, centre, name, fixed_atoms, size, basic_infos, zoom)



