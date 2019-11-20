#!/usr/bin/python3
import os
import sys
from copy import deepcopy
from Crystal import Geometry
from Common import Job
from Common import record
from Common import ReadIni
from Common import record_data_json
import HF1
import GeoOPt


def hf1(path, moni):

    rec = 'First Hartree Fock Calculation begins.\n'
    rec += '---' * 25
    print(rec)
    record(path, rec)

    # read info from input.ini file
    init_dist = HF1.read_init_dis(path)
    Ini = ReadIni()
    name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry, fixed_atoms = Ini.get_basic_info()
    geometry = Geometry(geometry=geometry)
    bs_type, nodes, crystal_path = Ini.get_hf1()
    cal_parameters = Ini.get_cal_parameters('HF1')
    if nodes == '' or nodes == 'default':
        nodes = 12
    record_data_json(path, 'basis_set', bs_type, section='hf1')
    record_data_json(path, 'nodes', nodes, section='hf1')

    jobs_GeoOpt = HF1.select_jobs(path)
    jobs_HF1 = []
    new_jobs = []
    hf1_jobs_finished = []
    # input for the whole system
    # print('number Geo Opt', len(jobs_GeoOpt))
    for job in jobs_GeoOpt:
        path_GeoOpt = job.path
        # Bilayer
        path_HF1 = path_GeoOpt.replace('geo_opt', 'hf1')
        new_job = Job(path_HF1)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Input(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type,
                layertype='bilayer',
                fiexed_atoms=fixed_atoms,
                cal_parameters=cal_parameters,
                geometry=geometry,
                lattice_parameters=lattice_parameter)
            Inp.gen_input()
            HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)
        # upperlayer
        path_upper = os.path.join(path_HF1, 'upperlayer')
        new_job = Job(path_upper)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Layer_Inp(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type,
                layertype='upperlayer',
                fiexed_atoms=fixed_atoms,
                cal_parameters=cal_parameters)
            Inp.gen_input()
            HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)
        # underlayer
        path_under = os.path.join(path_HF1, 'underlayer')
        new_job = Job(path_under)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Layer_Inp(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type,
                layertype='underlayer',
                fiexed_atoms=fixed_atoms,
                cal_parameters=cal_parameters)
            Inp.gen_input()
            HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)

    # Submit the calculation job
    hf1_jobs_finished_new = HF1.submit(new_jobs, nodes, crystal_path, moni)
    hf1_jobs_finished += hf1_jobs_finished_new

    # read calculation results
    HF1.read_all_results_hf1(hf1_jobs_finished, init_dist)

    # deal with not-converged jobs
    # jobs_not_converged = [job for job in hf1_jobs_finished if job.status == 'not converged']
    # hf1_jobs_finished = [job for job in hf1_jobs_finished if job.status != 'not converged']
    # # try to not use GUESSP
    # for job in jobs_not_converged:
    #     HF1.delete_guessp(job)
    # new_jobs_finished = HF1.submit(jobs_not_converged)
    # hf1_jobs_finished += new_jobs_finished
    # jobs_not_converged = [job for job in hf1_jobs_finished if job.status == 'not converged']
    # hf1_jobs_finished = [job for job in hf1_jobs_finished if job.status != 'not converged']
    # # if still not converged, try to change some parameters
    # while len(jobs_not_converged) > 0:
    #     HF1.change_parameters(jobs_not_converged)
    #     new_jobs_finished = HF1.submit(jobs_not_converged)
    #     hf1_jobs_finished += hf1_jobs_finished_new
    #     jobs_not_converged = [job for job in hf1_jobs_finished if job.status == 'not converged']
    #     hf1_jobs_finished = [job for job in hf1_jobs_finished if job.status != 'not converged']

    rec = 'HF1 finished!\n'
    rec += '***' * 25
    print(rec)
    record(path, rec)


def hf1_start(path, moni):

    rec = 'First Hartree Fock Calculation begins.\n'
    rec += '---' * 25
    print(rec)
    record(path, rec)

    # read infos from input.ini file
    Ini = ReadIni()
    name, slab_or_molecule, group, lattice_parameter, number_atoms, geometry, fixed_atoms = Ini.get_basic_info()
    distance_series, shift_series = Ini.get_series()
    cal_parameters = Ini.get_cal_parameters('Geo_Opt')
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
    bs_type, nodes, crystal_path = Ini.get_hf1()
    cal_parameters = Ini.get_cal_parameters('HF1')
    if nodes == '' or nodes == 'default':
        nodes = 12
    record_data_json(path, 'basis_set', bs_type, section='hf1')
    record_data_json(path, 'nodes', nodes, section='hf1')

    jobs_HF1 = []
    new_jobs = []
    hf1_jobs_finished = []
    # generation of the first INPUT
    dirname = 'x_0/z_0'
    job = os.path.join(path, 'hf1')
    job = os.path.join(job, dirname)
    job = Job(job)
    jobs_finished = []
    GeoOPt.write_init_dist(geometry, path)

    job_geo_dict = {job: geometry}
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
        Geo_with_diff_Dis_diff_Distance = GeoOPt.Range_of_Distances(
            geometry, distance_series)
        geo_with_diff_dis_diff_distance = Geo_with_diff_Dis_diff_Distance.get_geo_series()
        distances = sorted(geo_with_diff_dis_diff_distance.keys())
        loc = 3
        for i in range(len(distances)):
            if distances[i - 1] <= 0 and distances[i] >= 0:
                loc = i
        # Select the some of the distance values
        for key in list(geo_with_diff_dis_diff_distance.keys()):
            if key not in distances[loc - 2:loc + 2]:
                del geo_with_diff_dis_diff_distance[key]
        # print(list(geo_with_diff_dis_diff_distance.keys()))
        for distance, geo in geo_with_diff_dis_diff_distance.items():
            dirname = 'x_{0:.2f}/z_{1:.3f}'.format(shift, distance)
            new_path = os.path.join(path, os.path.join('geo_opt', dirname))
            new_job = Job(new_path)
            # print(new_job)
            job_geo_dict[new_job] = geo

    # generation all INPUT files
    for job, geometry in job_geo_dict.items():
        if not HF1.if_cal_finish(job):
            # print('JOB not finished yet: ', job)
            HF1_Inp = HF1.Input(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type,
                layertype='bilayer',
                fiexed_atoms=fixed_atoms,
                cal_parameters=cal_parameters,
                geometry=geometry,
                lattice_parameters=lattice_parameter)
            HF1_Inp.gen_input()
            HF1.copy_submit_scr(job, nodes, crystal_path)
            new_jobs.append(job)
        else:
            jobs_finished.append(job)
        jobs_HF1.append(job)
        # deal with layers
        # upperlayer
        path_upper = os.path.join(job.path, 'upperlayer')
        upper_job = Job(path_upper)
        if not HF1.if_cal_finish(upper_job):
            Inp = HF1.Layer_Inp(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type,
                layertype='upperlayer',
                fiexed_atoms=fixed_atoms,
                cal_parameters=cal_parameters,
                geometry=geometry,
                lattice_parameters=lattice_parameter)
            Inp.gen_input()
            HF1.copy_submit_scr(upper_job, nodes, crystal_path)
            new_jobs.append(upper_job)
        else:
            hf1_jobs_finished.append(upper_job)
        jobs_HF1.append(upper_job)
        # underlayer
        path_under = os.path.join(job.path, 'underlayer')
        under_job = Job(path_under)
        if not HF1.if_cal_finish(under_job):
            Inp = HF1.Layer_Inp(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type,
                layertype='underlayer',
                fiexed_atoms=fixed_atoms,
                cal_parameters=cal_parameters,
                geometry=geometry,
                lattice_parameters=lattice_parameter)
            Inp.gen_input()
            HF1.copy_submit_scr(under_job, nodes, crystal_path)
            new_jobs.append(under_job)
        else:
            hf1_jobs_finished.append(under_job)
        jobs_HF1.append(upper_job)

    # Submit the calculation job
    hf1_jobs_finished_new = HF1.submit(new_jobs, nodes, crystal_path, moni)
    hf1_jobs_finished += hf1_jobs_finished_new

    # read calculation results
    init_dist = HF1.read_init_dis(path)
    HF1.read_all_results_hf1(hf1_jobs_finished, init_dist)

    rec = 'HF1 finished!\n'
    rec += '***' * 25
    print(rec)
    record(path, rec)
