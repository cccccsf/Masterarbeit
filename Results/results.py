#!/usr/bin/python3
import os
from copy import deepcopy
from Common import Job_path
from Common import record
import Correction
from Correction import if_cal_finish
from Correction import Result
from HF1 import read_init_dis
import Results
import HF2
import RPA


def results(path):

    # get jobs
    correction_jobs, root_jobs = get_jobs(path)
    correction_jobs_dict = {}

    # read results of correction
    init_dist = read_init_dis(path)
    if not if_results_json_exits(path) and len(correction_jobs) != 0:
        Correction.read_all_results(correction_jobs, init_dist)
    correction_results = []
    for job in correction_jobs:
        CoRe = Results.CorrectionResult(job)
        correction_results.append(CoRe)

    # choose different correction resluts and catagorize by basis-set
    method_error_jobs = []
    method_error_dict = {}
    iext1_rpa_dict = {}
    bas_rpa_iext1_dict = {}
    for Res in correction_results:
        if Res.step == 'rpa_cc':
            method_error_jobs.append(Res)
            if Res.bs not in method_error_dict:
                method_error_dict[Res.bs] = {Res.coord: Res}
            else:
                method_error_dict[Res.bs][Res.coord] = Res
        elif Res.step == 'iext1_rpa':
            if Res.bs not in iext1_rpa_dict:
                iext1_rpa_dict[Res.bs] = {Res.coord: Res}
            else:
                iext1_rpa_dict[Res.bs][Res.coord] = Res
        elif Res.step == 'bas_rpa_iext1':
            if Res.bs not in bas_rpa_iext1_dict:
                bas_rpa_iext1_dict[Res.bs] = {Res.coord: Res}
            else:
                bas_rpa_iext1_dict[Res.bs][Res.coord] = Res
    coord_set = {job.coord for job in method_error_jobs}
    coord_list = list(coord_set)

    # get extraplation values
    extrap_method_error = {'avdtz': {}, 'avtqz': {}}
    extrap_iext1_rpa = {'avdtz': {}, 'avtqz': {}}
    basis_set_correction = {'avdtz': {}, 'avtqz': {}}
    for coord in coord_list:
        # method error correction
        if 'avdz' and 'avtz' in method_error_dict:
            if coord in method_error_dict['avdz'] and method_error_dict['avtz']:
                avdz = method_error_dict['avdz'][coord]
                avtz = method_error_dict['avtz'][coord]
                avdtz = deepcopy(avtz)
                avdtz.set_extrapolation_energy(avdz, avtz, [2, 3])
                avdtz.bs = 'av(d/t)z'
                extrap_method_error['avdtz'][coord] = avdtz
            # else:
            #     print(coord)
        if 'avtz' and 'avqz' in method_error_dict:
            if coord in method_error_dict['avtz'] and method_error_dict['avqz']:
                avtz = method_error_dict['avtz'][coord]
                avqz = method_error_dict['avqz'][coord]
                avtqz = deepcopy(avqz)
                avtqz.set_extrapolation_energy(avtz, avqz, [3, 4])
                avtqz.bs = 'av(t/q)z'
                extrap_method_error['avtqz'][coord] = avtqz
            # else:
            #     print(coord)
        # basis set correction
        # iext1
        if 'avdz' and 'avtz' in iext1_rpa_dict:
            if coord in iext1_rpa_dict['avdz'] and iext1_rpa_dict['avtz']:
                avdz = iext1_rpa_dict['avdz'][coord]
                avtz = iext1_rpa_dict['avtz'][coord]
                avdtz = deepcopy(avtz)
                avdtz.set_extrapolation_energy(avdz, avtz, [2, 3])
                avdtz.bs = 'av(d/t)z'
                extrap_iext1_rpa['avdtz'][coord] = avdtz
        if 'avtz' and 'avqz' in iext1_rpa_dict:
            if coord in iext1_rpa_dict['avtz'] and iext1_rpa_dict['avqz']:
                avtz = iext1_rpa_dict['avtz'][coord]
                avqz = iext1_rpa_dict['avqz'][coord]
                avtqz = deepcopy(avtz)
                avtqz.set_extrapolation_energy(avtz, avqz, [3, 4])
                avtqz.bs = 'av(t/q)z'
                extrap_iext1_rpa['avtqz'][coord] = avtqz
        # get basis set correction
        if len(extrap_iext1_rpa['avdtz']) != 0:
            if coord in extrap_iext1_rpa['avdtz'] and coord in bas_rpa_iext1_dict['per']:
                bs_correction = extrap_iext1_rpa['avdtz'][coord] - \
                    bas_rpa_iext1_dict['per'][coord]
                bs_correction.bs = 'av(d/t)z'
                basis_set_correction['avdtz'][coord] = bs_correction
        if len(extrap_iext1_rpa['avtqz']) != 0:
            if coord in extrap_iext1_rpa['avtqz'] and coord in bas_rpa_iext1_dict['per']:
                bs_correction = extrap_iext1_rpa['avtqz'][coord] - \
                    bas_rpa_iext1_dict['per'][coord]
                bs_correction.bs = 'av(t/q)z'
                basis_set_correction['avtqz'][coord] = bs_correction
    # record above data
    results_file = os.path.join(path, 'results.json')
    record_correction_results(
        basis_set_correction,
        coord_list,
        extrap_iext1_rpa,
        extrap_method_error,
        init_dist,
        results_file)

    # get Hartree Fock values
    hf2_json_file = os.path.join(path, 'hf2')
    hf2_json_file = os.path.join(hf2_json_file, 'hf2.json')
    hf2_coords = set()
    hf2_jobs = []
    for job in correction_jobs:
        if job.coord not in hf2_coords:
            job_path = job.path
            new_job_path = job_path.replace('cluster', 'hf2')
            new_job = Job_path(new_job_path)
            hf2_jobs.append(new_job)
            hf2_coords.add(new_job.coord)
    for job in hf2_jobs[:]:
        job_path = job.path
        under_path = os.path.join(job_path, 'underlayer')
        upper_path = os.path.join(job_path, 'upperlayer')
        under_job = Job_path(under_path)
        upper_job = Job_path(upper_path)
        hf2_jobs.append(under_job)
        hf2_jobs.append(upper_job)
    if not os.path.exists(hf2_json_file) and len(hf2_jobs) != 0:
        HF2.read_all_results_hf2(hf2_jobs, init_dist=init_dist)
    hf2 = {}
    for job in hf2_jobs:
        coord = str(job.coord)
        Res = Results.FResult(job)
        Res.read_info_from_json()
        if coord not in hf2:
            hf2[coord] = {}
        hf2[coord][job.layertype] = Res
    # calculate layer energy
    for coord in coord_list:
        layer_Res = hf2[coord]['bilayer'] - \
            hf2[coord]['upperlayer'] - hf2[coord]['underlayer']
        layer_Res.record_data('layer energy')
        layer_Res.record_data('hf', results_file)
        hf2[coord]['layer energy'] = layer_Res

    # get embedded fragment LdrCCD (RPA) values
    rpa_jobs = []
    for job in hf2_jobs:
        job_path = job.path
        new_job_path = job_path.replace('hf2', 'rpa')
        new_job = Job_path(new_job_path)
        rpa_jobs.append(new_job)
    rpa_json_file = os.path.join(path, 'rpa')
    rpa_json_file = os.path.join(rpa_json_file, 'rpa.json')
    if not os.path.exists(rpa_json_file) and len(rpa_jobs) != 0:
        RPA.read_and_record_all_results(rpa_jobs)
    rpa = {}
    for job in rpa_jobs:
        coord = str(job.coord)
        Res = Results.FResult(job)
        Res.read_info_from_json()
        if coord not in rpa:
            rpa[coord] = {}
        rpa[coord][job.layertype] = Res
    # calculate layer energy
    for coord in coord_list:
        layer_Res = rpa[coord]['bilayer'] - \
            rpa[coord]['upperlayer'] - rpa[coord]['underlayer']
        rpa[coord]['layer energy'] = layer_Res
        layer_Res.record_data('layer energy')
        layer_Res.record_data('rpa', results_file)

    # get final results
    final_data = {'avdtz': {}, 'avtqz': {}}
    for coord in coord_list:
        if len(extrap_method_error['avdtz']) != 0:
            final_data['avdtz'][coord] = hf2[coord]['layer energy'] + rpa[coord]['layer energy'] + \
                extrap_method_error['avdtz'][coord] + extrap_iext1_rpa['avdtz'][coord]
        if len(extrap_method_error['avtqz']) != 0:
            final_data['avtqz'][coord] = hf2[coord]['layer energy'] + rpa[coord]['layer energy'] + \
                extrap_method_error['avtqz'][coord] + extrap_iext1_rpa['avtqz'][coord]
    # record data
    for coord in coord_list:
        try:
            Results.record_data_json(
                final_data['avdtz'][coord],
                'final reslut avdtz',
                results_file,
                init_dist)
        except Exception as e:
            print(e)
        try:
            Results.record_data_json(
                final_data['avtqz'][coord],
                'final reslut avtqz',
                results_file,
                init_dist)
        except Exception as e:
            print(e)

    print('Data processing finished!!!')
    record(path, 'Data processing finished!!!')


def record_correction_results(
        basis_set_correction,
        coord_list,
        extrap_iext1_rpa,
        extrap_method_error,
        init_dist,
        results_file):
    for coord in coord_list:
        try:
            Results.record_data_json(
                extrap_method_error['avdtz'][coord],
                'method error avdtz',
                results_file,
                init_dist)
        except KeyError:
            pass
        try:
            Results.record_data_json(
                extrap_method_error['avtqz'][coord],
                'method error avtqz',
                results_file,
                init_dist)
        except KeyError:
            pass
        try:
            Results.record_data_json(
                extrap_iext1_rpa['avdtz'][coord],
                'avdtz_iext1_rpa',
                results_file,
                init_dist)
        except KeyError:
            pass
        try:
            Results.record_data_json(
                extrap_iext1_rpa['avtqz'][coord],
                'avtqz_iext1_rpa',
                results_file,
                init_dist
            )
        except KeyError:
            pass
        try:
            Results.record_data_json(
                basis_set_correction['avdtz'][coord],
                'avdtz basis set correction',
                results_file,
                init_dist
            )
        except KeyError:
            pass
        try:
            Results.record_data_json(
                basis_set_correction['avtqz'][coord],
                'avtqz basis set correction',
                results_file,
                init_dist
            )
        except KeyError:
            pass


def if_results_json_exits(path):
    cluster_path = os.path.join(path, 'cluster')
    results_file = os.path.join(cluster_path, 'results.json')
    if os.path.exists(results_file):
        return True
    return False


def get_jobs(path):
    path = os.path.join(path, 'cluster')
    walks = os.walk(path)
    jobs = set()
    root_jobs = set()
    for root, dirs, files in walks:
        if len(files) > 0:
            for file in files:
                if os.path.splitext(file)[-1] == '.out':
                    new_job = Job_path(root)
                    new_job.method = os.path.splitext(file)[0]
                    if if_cal_finish(new_job) and new_job not in jobs:
                        jobs.add(new_job)
                        root_jobs.add(Job_path(root))
    jobs = list(jobs)
    root_jobs = list(root_jobs)
    return jobs, root_jobs
