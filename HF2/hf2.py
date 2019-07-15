#!/usr/bin/python3
import HF2
from Common import record
from Common import ReadIni
from Common import Job
from HF1 import read_init_dis
from Common import record_data_json


def hf2(path):

    rec = 'Second Hartree Fock Calculation begins.\n'
    rec += '---'*25
    print(rec)
    record(path, rec)

    init_dist = read_init_dis(path)
    # read basic computation information
    jobs_HF1 = HF2.get_jobs(path)
    Ini = ReadIni()
    name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry, fixed_atoms = Ini.get_basic_info()
    bs_type, nodes, crystal_path = Ini.get_hf2()
    cal_parameters = Ini.get_cal_parameters('HF2')
    aos = Ini.get_aos()
    if nodes == '' or nodes == 'default':
        nodes = 12
    record_data_json(path, 'basis_set', bs_type, section='hf2')
    record_data_json(path, 'nodes', nodes, section='hf2')

    # categorization
    bilayer = []
    singlelayer = []
    for job in jobs_HF1:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)
<<<<<<< HEAD:venv/HF2/hf2.py
    
    #generation of all input files
=======

    # generation of all input files
<<<<<<< HEAD
>>>>>>> 9837390163629d9445152c2c968b8f8c2d249d30:HF2/hf2.py
    for job in bilayer:
        Inp = HF2.Input(
            job,
            name,
            slab_or_molecule,
            group,
            bs_type=bs_type,
            layertype='bilayer',
            fixed_atoms=fixed_atoms)
        Inp.gen_input()
        HF2.copy_submit_scr(job, nodes, crystal_path)
        HF2.copy_fort9(job)
    for job in singlelayer:
        Inp = HF2.Layer_Inp(
            job,
            name,
            slab_or_molecule,
            group,
            bs_type=bs_type,
            layertype=job.layertype,
            fixed_atoms=fixed_atoms)
        Inp.gen_input()
        HF2.copy_submit_scr(job, nodes, crystal_path)
        HF2.copy_fort9(job)
<<<<<<< HEAD:venv/HF2/hf2.py
    
    #submit the jobs
=======

    # submit the jobs
>>>>>>> 9837390163629d9445152c2c968b8f8c2d249d30:HF2/hf2.py
=======
>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
    hf2_jobs = []
    hf2_jobs_finished = []
    for job in bilayer:
        new_path = job.path
        new_path = new_path.replace('hf1', 'hf2')
        new_job = Job(new_path)
        if not HF2.if_cal_finish(new_job):
            Inp = HF2.Input(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type=bs_type,
                layertype='bilayer',
                fixed_atoms=fixed_atoms,
                cal_parameters=cal_parameters,
                aos=aos)
            Inp.gen_input()
            HF2.copy_submit_scr(job, nodes, crystal_path)
            # HF2.copy_fort9(job)
            hf2_jobs.append(new_job)
        else:
            hf2_jobs_finished.append(new_job)
    for job in singlelayer:
        new_path = job.path
        new_path = new_path.replace('hf1', 'hf2')
        new_job = Job(new_path)
        if not HF2.if_cal_finish(new_job):
            Inp = HF2.Layer_Inp(
                job,
                name,
                slab_or_molecule,
                group,
                bs_type=bs_type,
                layertype=job.layertype,
                fixed_atoms=fixed_atoms,
                cal_parameters=cal_parameters,
                aos=aos)
            Inp.gen_input()
            HF2.copy_submit_scr(job, nodes, crystal_path)
            # HF2.copy_fort9(job)
            hf2_jobs.append(new_job)
        else:
            hf2_jobs_finished.append(new_job)

    # submit the jobs
    if len(hf2_jobs) > 0:
        new_finished_jobs = HF2.submit(hf2_jobs)
        hf2_jobs_finished += new_finished_jobs

    # read calculation results
    if len(hf2_jobs_finished) > 0:
        HF2.read_all_results_hf2(hf2_jobs_finished, init_dist=init_dist)

<<<<<<< HEAD
    print('Hartree Fock calculation 2 finished!!!')
    recod(path, 'Hartree Fock calculation 2 finished!!!')
=======
    rec = 'HF2 finished!\n'
    rec += '***'*25
    print(rec)
    record(path, rec)


>>>>>>> a683a8af38ab42158c09693bb6677e091cd66cad
