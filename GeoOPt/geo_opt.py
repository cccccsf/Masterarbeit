#!/usr/bin/python3
import os
from copy import deepcopy
from Crystal import Geometry
from Common import Job
from Common import record
from Common import ReadIni
from Common import look_for_in_list
from Common import record_data_json
import GeoOPt
from GeoOPt import if_cal_finish


def geo_opt(path):

    rec = 'Geometry Optimization begins.'
    print(rec)
    record(path, rec)
    GeoOPt.creat_geo_lat_json(path)     # might be deleted

    # read infos from input.ini file
    Ini = ReadIni()
    name, slab_or_molecule, group, lattice_parameter, number_atoms, geometry, fixed_atoms = Ini.get_basic_info()
    distance_series, shift_series = Ini.get_series()
    record_data_json(path, 'project_name', name)
    record_data_json(path, 'system_type', slab_or_molecule)
    record_data_json(path, 'lattice_parameter', lattice_parameter)
    record_data_json(path, 'geometry', geometry)
    record_data_json(path, 'fixed_atoms', fixed_atoms)
    if isinstance(fixed_atoms, list) and len(fixed_atoms) == 2:
        geometry = Geometry(geometry=geometry, fixed_atoms=fixed_atoms)
    else:
        geometry = Geometry(geometry=geometry)
    original_geometry = deepcopy(geometry)
    bs_type, functional, nodes, crystal_path = Ini.get_geo_opt()
    record_data_json(path, 'basis_set', bs_type, section='geo_opt')
    record_data_json(path, 'functional', functional, section='geo_opt')
    record_data_json(path, 'nodes', nodes, section='geo_opt')
    test_ini_read(group, lattice_parameter, number_atoms, slab_or_molecule)

    jobs = []
    new_jobs = []
    # generation of the first INPUT
    dirname = 'x_0/z_0'
    job = os.path.join(path, 'geo_opt')
    job = os.path.join(job, dirname)
    job = Job(job)
    jobs_finished = []
    if not if_cal_finish(job):
        Geo_Inp = GeoOPt.Geo_Opt_Input(
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
    GeoOPt.write_init_dist(geometry, path)

    job_geo_dict = {}
    # Generation of the job with different layer distance
    diff_distances = GeoOPt.Range_of_Distances(geometry, distance_series)
    geo_with_diff_distance = diff_distances.get_geo_series()
    init_distance = diff_distances.init_distance
    for distance, geometry in geo_with_diff_distance.items():
        new_job = deepcopy(job)
        new_z_dirname = 'z_{0:.3f}'.format(distance)
        new_job.reset('z_dirname', new_z_dirname)
        job_geo_dict[new_job] = geometry

    # Generation of the job with different displacement, produce ((0.1, 0),
    # (0.25, 0), (0.35, 0), (0.5, 0))
    range_of_displacement = GeoOPt.Range_of_Displacement(
        original_geometry, shift_series)
    geo_with_diff_displacement = range_of_displacement.get_geo_series()
    job_geo_dict_dis = {}
    for displacement, geometry in geo_with_diff_displacement.items():
        new_job = deepcopy(job)
        new_x_dirname = 'x_{0:.2f}'.format(displacement)
        new_job.reset('x_dirname', new_x_dirname)
        job_geo_dict_dis[new_job] = geometry
        job_geo_dict[new_job] = geometry

    # generate jobs with various distance under different relatvie shifts
    for shift, geometry in geo_with_diff_displacement.items():
        Geo_with_diff_Dis_diff_Distance = GeoOPt.Range_of_Distances(geometry, distance_series)
        geo_with_diff_dis_diff_distance = Geo_with_diff_Dis_diff_Distance.get_geo_series()
        distances = list(geo_with_diff_dis_diff_distance.keys())
        distances.sort()
        loc = 3
        for i in range(len(distances)):
            if distances[i-1] <= 0 and distances[i] >= 0:
                loc = i
        # Select the some of the distance values
        for key in list(geo_with_diff_dis_diff_distance.keys()):
            if key not in distances[loc-2:loc+2]:
                del geo_with_diff_dis_diff_distance[key]
        # print(list(geo_with_diff_dis_diff_distance.keys()))
        for distance, geo in geo_with_diff_dis_diff_distance.items():
            dirname = 'x_{0:.2f}/z_{1:.3f}'.format(shift, distance)
            new_path = os.path.join(path, os.path.join('geo_opt', dirname))
            new_job = Job(new_path)
            print(new_job)
            job_geo_dict[new_job] = geo

    # generation all INPUT files besides the first one above
    for job, geometry in job_geo_dict.items():
        if not if_cal_finish(job):
            # print('JOB not finished yet: ', job)
            Geo_Inp = GeoOPt.Geo_Opt_Input(
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
    new_jobs_finished = GeoOPt.submit(
        new_jobs, nodes, crystal_path)
    jobs_finished += new_jobs_finished

    # # Select the optimal distance of each x point
    # para = [
    #     name,
    #     slab_or_molecule,
    #     group,
    #     lattice_parameter,
    #     bs_type,
    #     functional,
    #     nodes,
    #     crystal_path]
    # # x_10
    # x_10 = {job: geometry for job, geometry in job_geo_dict_dis.items()
    #         if job.x == '0.10'}
    # jobs_10 = [job for job in job_geo_dict_dis.keys() if job.x == '0.10']
    # init_job_10 = jobs_10[0]
    # jobs_10, x_10, min_job_10, jobs_10_finished = GeoOPt.select_optimal_dist(
    #     x_10, 0, para)
    # jobs += jobs_10
    # # x_25
    # x_25 = {job: geometry for job, geometry in job_geo_dict_dis.items()
    #         if job.x == '0.25'}
    # jobs_25 = [job for job in job_geo_dict_dis.keys() if job.x == '0.25']
    # init_job_25 = jobs_25[0]
    # pos_min_10 = look_for_in_list(jobs_10, min_job_10)
    # pos_init_10 = look_for_in_list(jobs_10, init_job_10)
    # diff = pos_min_10 - pos_init_10
    # jobs_25, x_25, min_job_25, jobs_25_finished = GeoOPt.select_optimal_dist(
    #     x_25, diff, para)
    # jobs += jobs_25
    # # x_35
    # x_35 = {job: geometry for job, geometry in job_geo_dict_dis.items()
    #         if job.x == '0.35'}
    # init_job_35 = list(x_35.keys())[0]
    # pos_min_25 = look_for_in_list(jobs_25, min_job_25)
    # pos_init_25 = look_for_in_list(jobs_25, init_job_25)
    # diff = pos_min_25 - pos_init_25
    # jobs_35, x_35, min_job_35, jobs_35_finished = GeoOPt.select_optimal_dist(
    #     x_35, diff, para)
    # jobs += jobs_35
    # # x_50
    # x_50 = {job: geometry for job, geometry in job_geo_dict_dis.items()
    #         if job.x == '0.50'}
    # init_job_50 = list(x_50.keys())[0]
    # pos_min_35 = look_for_in_list(jobs_35, min_job_35)
    # pos_init_35 = look_for_in_list(jobs_35, init_job_35)
    # diff = pos_min_35 - pos_init_35
    # jobs_50, x_50, min_job_50, jobs_50_finished = GeoOPt.select_optimal_dist(
    #     x_50, diff, para)
    # jobs += jobs_50
    #
    # # read calculation results
    # jobs_finished += jobs_10_finished
    # jobs_finished += jobs_25_finished
    # jobs_finished += jobs_35_finished
    # jobs_finished += jobs_50_finished
    GeoOPt.read_all_results(jobs_finished, init_distance)

    rec = 'Geometry optimization finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)


def test_ini_read(group_type, lattice_parameter, number_atoms, system_type):
    assert system_type == 'SLAB'
    assert group_type == 1
    assert number_atoms == 8
    assert lattice_parameter == [[3.27, 4.36], [90.0]]
