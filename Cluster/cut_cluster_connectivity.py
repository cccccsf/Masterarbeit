#!/usr/bin/python3
import math
import os
from Cluster import ClusterCutter
from Common import Job
from Common import mkdir
from Cluster.read_info import read_and_write_infos
from Cluster.atom import Atom
from Data.Periodict_Table import periodic_table_rev
from Data import read_cov_rad
from Common import Point



class ClusterCutterConec(ClusterCutter):

    def __init__(self, job, centre = [], name = '', fixed_atoms=None, size='S', basic_infos=[], zoom=1):
        super().__init__(job, centre, name, fixed_atoms, size, basic_infos, zoom)



