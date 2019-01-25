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
import HF1



def hf1(path):

    rec = 'First Hartree Fock Calculation begins...'
    print(rec)
    record(path, rec)

    ini_path = os.path.join(path, 'input.ini')
    ini_file = os.path.exists(ini_file)

    #read basic computation infomation
    if ini_file:
        jobs_GeoOpt = HF1.select_jobs(path)

        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        bs_type, nodes = Ini.get_hf1_info()
        if nodes == '' or nodes == 'default':
            nodes = 14
    else:
        print('Initilization file input.ini not found!')
        print('Please check it in the work directory!')
        print('Programm exit and Please reatart it from HF1 step.')
        sys.exit()

        if hf1_bs_type == 'default':
            if_bs_change = 0

        else:
            if_bs_change = 1
            Bs_Init = Initialization.Bs_Init(geometry, bs_type=hf1_bs_type)
            ele_to_bs_type, elements = Bs_Init.gen_bs_info(if_bs_change)

    #input for the whole system
    for job_dir in job_dirs:
        if if_bs_change == 0:
            Input = generation_of_input.Gen_Inp(job_dir)
            if Input.x_dirname == '0':
                Input.gen_input_init()
            else:
                Input.gen_input()
        elif if_bs_change == 1:
            Input = generation_of_input.Gen_Inp(job_dir, if_bs_change=1, ele_to_bs_type=ele_to_bs_type, elements=elements)
            if Input.x_dirname == '0':
                Input.gen_input_init()
            else:
                Input.gen_input()
        #copy submit file to the directory
        x = float(Input.x_dirname.split('_')[-1])
        if x == 0:
            init = 1
        else:
            init = 0
        dirname = Input.x_dirname + '/' + Input.z_dirname
        submit_job_hf1.copy_submit_scr(path, dirname, init)


    #input for underlayer
    for job_dir in job_dirs:
        if if_bs_change == 0:
            Under_Inp = input_of_layers.Under_Layer_Inp(job_dir)
            if Under_Inp.x_dirname == '0':
                Under_Inp.write_underlayer_inp_init()
            else:
                Under_Inp.write_underlayer_inp()
        elif if_bs_change == 1:
            Under_Inp = input_of_layers.Under_Layer_Inp(job_dir, if_bs_change=1, ele_to_bs_type=ele_to_bs_type, elements=elements)
            if Under_Inp.x_dirname == '0':
                Under_Inp.write_underlayer_inp_init()
            else:
                Under_Inp.write_underlayer_inp()
        #copy submit file to the directory
        x = float(Input.x_dirname.split('_')[-1])
        if x == 0:
            init = 1
        else:
            init = 0
        dirname = Input.x_dirname + '/' + Input.z_dirname + '/underlayer'
        submit_job_hf1.copy_submit_scr(path, dirname, init)

    #input for upperlayer
    for job_dir in job_dirs:
        if if_bs_change == 0:
            Upper_Inp = input_of_layers.Upper_Layer_Inp(job_dir)
            if Upper_Inp.x_dirname == '0':
                Upper_Inp.write_upperlayer_inp_init()
            else:
                Upper_Inp.write_upperlayer_inp()
        elif if_bs_change == 1:
            Upper_Inp = input_of_layers.Upper_Layer_Inp(job_dir, if_bs_change=1, ele_to_bs_type=ele_to_bs_type, elements=elements)
            if Upper_Inp.x_dirname == '0':
                Upper_Inp.write_upperlayer_inp_init()
            else:
                Upper_Inp.write_upperlayer_inp()
        #copy submit file to the directory
        x = float(Input.x_dirname.split('_')[-1])
        if x == 0:
            init = 1
        else:
            init = 0
        dirname = Input.x_dirname + '/' + Input.z_dirname + '/upperlayer'
        submit_job_hf1.copy_submit_scr(path, dirname, init)

    #Submit the calculation job
    hf1_job_dirs = submit_job_hf1.get_job_dirs(path)
    #submitted_jobs_hf1 = submit_job.submit(job_dirs)

    #read calculation results
    read_results_hf1.read_all_results(job_dirs)
    read_results.write_init_distance(path, init_distance)

    print('Hartree Fock calculation 1 finished!!!')
