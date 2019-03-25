#!/usr/bin/python3
import os
import sys
import Initialization
from copy import deepcopy
from Crystal import Geometry
from Common import mkdir
from Common import Job_path
from Common import record
from Common import ReadIni
from Common import look_for_in_list
import geometry_optimization
from geometry_optimization import if_cal_finish


def geo_opt(path):

    rec = 'Geometry Optimization begins...'
    print(rec)
    record(path, rec)
    geometry_optimization.creat_geo_lat_json(path)

    ini_path = os.path.dirname(__file__)
    ini_path = os.path.dirname(ini_path)
    file = os.path.join(ini_path, 'input.ini')
    file = os.path.exists(file)

    if file:
        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        geometry = Ini.get_geometry()
        if isinstance(fixed_atoms, list) and len(fixed_atoms) == 2:
            geometry = Geometry(geometry=geometry, fixed_atoms=fixed_atoms)
        else:
            geometry = Geometry(geometry=geometry)
        original_geometry = deepcopy(geometry)
        bs_type, functional, nodes, crystal_path = Ini.get_geo_opt_info()

    else:
        print('INPUT file does not exist!!!')
        print('''Do you want to start initialization or exit?
                 Please enter 1 to start initialization programm and enter 0 to exit the programm''')
        while True:
            init_or_exit = input()
            if init_or_exit == 1 or 0:
                if init_or_exit == 1:
                    # geometry init
                    Geo_Init = Initialization.Geo_Init()
                    name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info = Geo_Init.initialization()
                    # basis set init
                    Bs_Init = Initialization.Bs_Init(geometry_info)
                    if_bs_change, ele_to_bs_type, elements = Bs_Init.initialization()
                    # calculation input
                    Cal_Init = Initialization.Cal_Init()
                    functional = Cal_Init.functional_init()
                elif init_or_exit == 0:
                    try:
                        sys.exit(1)
                    except BaseException:
                        print('Program Exits.')
                    finally:
                        print(
                            '---------------------------------------------------------------------------------------')
                break
            else:
                print('Please enter the right number!!')

    sys.exit()
    jobs = []
    new_jobs = []
    # generation of the first INPUT
    dirname = 'x_0/z_0'
    job = os.path.join(path, 'geo_opt')
    job = os.path.join(job, dirname)
    job = Job_path(job)
    jobs_finished = []
    if not if_cal_finish(job):
        Geo_Inp = geometry_optimization.Geo_Opt_Input(
            job,
            name,
            slab_or_molecule,
            group,
            lattice_parameter,
            geometry,
            bs_type,
            functional)
        Geo_Inp.gen_input()
        new_jobs.append(job)
    else:
        jobs_finished.append(job)
    jobs.append(job)
    geometry_optimization.write_init_dist(geometry, path)

    job_geo_dict = {}
    # Generation of the job with different layer distance
    diff_distances = geometry_optimization.Range_of_Distances(geometry, job)
    geo_with_diff_distance = diff_distances.get_geo_series()
    init_distance = diff_distances.init_distance

    for distance, geometry in geo_with_diff_distance.items():
        new_job = deepcopy(job)
        new_z_dirname = 'z_{0:.3f}'.format(distance)
        new_job.reset('z_dirname', new_z_dirname)
        job_geo_dict[new_job] = geometry

    # Generation of the job with different displacement, produce ((0.1, 0),
    # (0.25, 0), (0.35, 0), (0.5, 0))
    range_of_displacement = geometry_optimization.Range_of_Displacement(
        original_geometry, job)
    geo_with_diff_displacement = range_of_displacement.get_geo_series()
    job_geo_dict_dis = {}

    for displacement, geometry in geo_with_diff_displacement.items():
        new_job = deepcopy(job)
        new_x_dirname = 'x_{0:.2f}'.format(displacement)
        new_job.reset('x_dirname', new_x_dirname)
        job_geo_dict_dis[new_job] = geometry
        job_geo_dict[new_job] = geometry

    # generation all INPUT files besides the first one above
    for job, geometry in job_geo_dict.items():
        if not if_cal_finish(job):
            #print('JOB not finished yet: ', job)
            Geo_Inp = geometry_optimization.Geo_Opt_Input(
                job,
                name,
                slab_or_molecule,
                group,
                lattice_parameter,
                geometry,
                bs_type,
                functional)
            Geo_Inp.gen_input()
            new_jobs.append(job)
        else:
            jobs_finished.append(job)
        jobs.append(job)
    # Copy files and Submit the calculation job above
    new_jobs_finished = geometry_optimization.submit(
        new_jobs, nodes, crystal_path)
    jobs_finished += new_jobs_finished

    # Select the optimal distance of each x point
    para = [
        name,
        slab_or_molecule,
        group,
        lattice_parameter,
        bs_type,
        functional,
        nodes,
        crystal_path]
    # x_10
    x_10 = {job: geometry for job, geometry in job_geo_dict_dis.items()
            if job.x == '0.10'}
    jobs_10 = [job for job in job_geo_dict_dis.keys() if job.x == '0.10']
    init_job_10 = jobs_10[0]
    jobs_10, x_10, min_job_10, jobs_10_finished = geometry_optimization.select_optimal_dist(
        x_10, 0, para)
    jobs += jobs_10
    # x_25
    x_25 = {job: geometry for job, geometry in job_geo_dict_dis.items()
            if job.x == '0.25'}
    jobs_25 = [job for job in job_geo_dict_dis.keys() if job.x == '0.25']
    init_job_25 = jobs_25[0]
    pos_min_10 = look_for_in_list(jobs_10, min_job_10)
    pos_init_10 = look_for_in_list(jobs_10, init_job_10)
    diff = pos_min_10 - pos_init_10
    jobs_25, x_25, min_job_25, jobs_25_finished = geometry_optimization.select_optimal_dist(
        x_25, diff, para)
    jobs += jobs_25
    # x_35
    x_35 = {job: geometry for job, geometry in job_geo_dict_dis.items()
            if job.x == '0.35'}
    init_job_35 = list(x_35.keys())[0]
    pos_min_25 = look_for_in_list(jobs_25, min_job_25)
    pos_init_25 = look_for_in_list(jobs_25, init_job_25)
    diff = pos_min_25 - pos_init_25
    jobs_35, x_35, min_job_35, jobs_35_finished = geometry_optimization.select_optimal_dist(
        x_35, diff, para)
    jobs += jobs_35
    # x_50
    x_50 = {job: geometry for job, geometry in job_geo_dict_dis.items()
            if job.x == '0.50'}
    init_job_50 = list(x_50.keys())[0]
    pos_min_35 = look_for_in_list(jobs_35, min_job_35)
    pos_init_35 = look_for_in_list(jobs_35, init_job_35)
    diff = pos_min_35 - pos_init_35
    jobs_50, x_50, min_job_50, jobs_50_finished = geometry_optimization.select_optimal_dist(
        x_50, diff, para)
    jobs += jobs_50

    # read calculation results
    jobs_finished += jobs_10_finished
    jobs_finished += jobs_25_finished
    jobs_finished += jobs_35_finished
    jobs_finished += jobs_50_finished
    geometry_optimization.read_all_results(jobs_finished, init_distance)

    print('Geometry optimization finished!!!')
    record(path, 'Geometry optimization finished!!!')
