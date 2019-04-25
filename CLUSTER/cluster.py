#!/usr/bin/python3
import os
from Common import Job_path
from Common import mkdir
from HF1 import read_init_dis
from RPA.submit_job_rpa import if_cal_finish
from CLUSTER import Cluster

def cluster(path):

    rec = 'Cluster Cutting begins...'
    print(rec)
    record(path, rec)

    init_dist = read_init_dis(path)
    ini_path = os.path.dirname(os.path.relpath(__file__))
    ini_path = os.path.dirname(ini_path)
    ini_file = os.path.join(ini_path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read parameters from ini file
    if ini_file:
        rpa_jobs = RPA.get_jobs(path)
        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        size, center_atoms, factors = Ini.get_cluster_info()
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

    #catagorization
    bilayer = []
    singlelayer = []
    for job in rpa_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    #generate clusters
    cluster_path = os.path.join(path, 'cluster')
    mkdir(cluster_path)
    Cluster.creat_json_file(cluster_path)
    for job in bilayr:
        Clu = Cluster(job, centre=center_atoms, name=name, size=size, fixed_atoms=fixed_atoms, factors=factors)
        Clu.write_xyz()

    print('Clusters generated!!!')
    record(path, 'Clusters generated!!!')



def get_jobs(path):
    path = os.path.join(path, 'rpa')
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'rpa.out' in files:
            new_job = Job_path(root)
            if if_cal_finish(new_job):
                jobs.append(new_job)
    return jobs
