#!/usr/bin/python3
import os
import sys
from Crystal import Geometry
from Common import Job
from Common import record
from Common import ReadIni
from Common import record_data_json
import HF1


def hf1(path, moni):

    rec = 'First Hartree Fock Calculation begins.\n'
    rec += '---'*25
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
            Inp = HF1.Input(job, name, slab_or_molecule, group, bs_type, layertype='bilayer', fiexed_atoms=fixed_atoms, cal_parameters=cal_parameters, geometry=geometry, lattice_parameters=lattice_parameter)
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
            Inp = HF1.Layer_Inp(job, name, slab_or_molecule, group, bs_type, layertype='upperlayer', fiexed_atoms=fixed_atoms, cal_parameters=cal_parameters)
            Inp.gen_input()
            # HF1.copy_submit_scr(new_job, nodes, crystal_path)
            new_jobs.append(new_job)
        else:
            hf1_jobs_finished.append(new_job)
        jobs_HF1.append(new_job)
        # underlayer
        path_under = os.path.join(path_HF1, 'underlayer')
        new_job = Job(path_under)
        if not HF1.if_cal_finish(new_job):
            Inp = HF1.Layer_Inp(job, name, slab_or_molecule, group, bs_type, layertype='underlayer', fiexed_atoms=fixed_atoms, cal_parameters=cal_parameters)
            Inp.gen_input()
            # HF1.copy_submit_scr(new_job, nodes, crystal_path)
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
    rec += '***'*25
    print(rec)
    record(path, rec)
