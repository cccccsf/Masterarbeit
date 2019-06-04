#!/usr/bin/python3
import os
from Common import Job
from Common import mkdir
from Common import record
from Common import ReadIni
from Common import record_data_json
from RPA.submit_job_rpa import if_cal_finish
import Cluster


def cluster(path):

    rec = 'Cluster Cutting begins.\n'
    rec += '---' * 25
    print(rec)
    record(path, rec)

    # read parameters from ini file
    Ini = ReadIni()
    name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry, fixed_atoms = Ini.get_basic_info()
    center_atoms, factors, deleted_atoms, coord, add_h, out_layer_number = Ini.get_cluster()
    cutting_setting = [coord, add_h]
    record_data_json(path, 'central atoms', center_atoms, section='cluster')
    record_data_json(path, 'cutting factors', factors, section='cluster')
    record_data_json(path, 'deleted atoms', deleted_atoms, section='cluster')
    cutting_setting_dict = {'coord': coord, 'add_h': add_h, 'out_layer_number': out_layer_number}
    record_data_json(path, 'cutting setting', cutting_setting_dict, section='cluster')

    # get bilayer jobs
    rpa_jobs = get_jobs(path)
    cluster_jobs = [job for job in rpa_jobs if job.layertype == 'bilayer']
    for job in cluster_jobs:
        if 'rpa' in job.path:
            job.path = job.path.replace('rpa', 'cluster')
        elif 'geo_opt' in job.path:
            job.path = job.path.replace('geo_opt', 'cluster')
        job.method = 'cluster'

    # generate clusters
    cluster_path = os.path.join(path, 'cluster')
    mkdir(cluster_path)
    Cluster.creat_json_file(cluster_path)
    for job in cluster_jobs:
        Clu = Cluster.ClusterCutter(
            job,
            center=center_atoms,
            name=name,
            fixed_atoms=fixed_atoms,
            factors=factors,
            cutting_setting=cutting_setting,
            deleted_atoms=deleted_atoms)
        if not Cluster.if_cluster_already_generated(job):
            Clu.get_cluster()
            if out_layer_number is True:
                Clu.write_xyz_with_layernumber()
            else:
                Clu.write_xyz()

    rec = 'Cluster Cutting finished!\n'
    rec += '***' * 25
    print(rec)
    record(path, rec)


def get_jobs(path):
    path = os.path.join(path, 'rpa')
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'rpa.out' in files:
            new_job = Job(root)
            if if_cal_finish(new_job):
                jobs.append(new_job)
    # directly select job from geo_opt directory
    if len(jobs) == 0:
        path = path.replace('rpa', 'geo_opt')
        for root, dirs, files in os.walk(path):
            if 'geo_opt.out' in files or 'hf.out' in files:
                new_job = Job(root)
                jobs.append(new_job)
    return jobs
