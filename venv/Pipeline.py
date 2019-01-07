#!/usr/bin/python3
import os
import sys
import Initialization
from geometry_optimization import gen_input
from geometry_optimization import gen_displacement_series
from geometry_optimization import read_input
from geometry_optimization import submit_job
from geometry_optimization import read_results
from Common.file_processing import mkdir
from Common.job_path import Job_path
from HF1 import generation_of_input
from HF1 import input_of_layers
from HF1 import submit_job_hf1
from HF1 import read_results_hf1
from HF1.read_results_hf1 import get_x_z_and_layertype
import Localization
import HF2


def geo_opt(path):

    #path = os.getcwd()
    file = os.path.exists('INPUT')

    if file:
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info, bs_type, functional = read_input.read_input(path)
        if bs_type == 'END':
            if_bs_change = 0
            bs_type = 'default'
        else:
            if_bs_change = 1
        Bs_Init = Initialization.Bs_Init(geometry_info, bs_type)
        ele_to_bs_type, elements = Bs_Init.gen_bs_info(if_bs_change)
        #print(elements)
        #print(ele_to_bs_type)
    else:
        print('INPUT file does not exist!!!')
        print('''Do you want to start initialization or exit?
                 Please enter 1 to start initialization programm and enter 0 to exit the programm''')
        while True:
            init_or_exit = input()
            if init_or_exit == 1 or 0:
                if init_or_exit == 1:
                    #geometry init
                    Geo_Init = Initialization.Geo_Init()
                    name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info = Geo_Init.initialization()
                    #basis set init
                    Bs_Init = Initialization.Bs_Init(geometry_info)
                    if_bs_change, ele_to_bs_type, elements = Bs_Init.initialization()
                     #calculation input
                    Cal_Init = Initialization.Cal_Init()
                    functional = Cal_Init.functional_init()
                elif init_or_exit == 0:
                    try:
                        sys.exit(1)
                    except:
                        print('Program Exits.')
                    finally:
                        print('---------------------------------------------------------------------------------------')
                break
            else:
                print('Please enter the right number!!')

    #generation of the first INPUT
    dirname = 'x_0/z_0'
    Geo_Inp = gen_input.Geometry_Input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry_info, dirname)
    Geo_Inp.gen_input()
    #optimization input
    Opt_Inp = gen_input.Opt_Input(path, number_of_atoms, geometry_info, dirname)
    Opt_Inp.write_opt_info()
    fixed_atoms = Opt_Inp.fixed_atoms
    #basis set input
    #print(path, ele_to_bs_type, dirname, if_bs_change)
    Bs_Inp = gen_input.Basis_Set_Input(path, ele_to_bs_type, dirname, if_bs_change)
    Bs_Inp.write_basis_set()
    #calculation input
    Cal_Inp = gen_input.Cal_Input(path, elements, dirname, functional)
    Cal_Inp.write_cal_input_init()
    submit_job.copy_submit_scr(path, dirname, init=1)

    #Generation of the INPUTs with different layer distance
    Range_of_Distance = gen_displacement_series.Range_of_Distances(geometry_info, fixed_atoms)
    geo_with_diff_distance = Range_of_Distance.get_geo_series()
    init_distance = Range_of_Distance.init_distance

    #print(geo_with_diff_distance)
    for distance, geometry in geo_with_diff_distance.items():
        dirname = 'x_0/z_{0:.3f}'.format(distance)
        #print(dirname)
        gen_input.write_input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry, ele_to_bs_type, elements, functional, dirname, if_bs_change, init=1)
        submit_job.copy_submit_scr(path, dirname, init=1)

    #Generation of the INPUTs with different displacement
    range_of_displacement = gen_displacement_series.Range_of_Displacement(geometry_info, fixed_atoms)
    geo_with_diff_displacement = range_of_displacement.get_geometry_series()
    for displace, geometry in geo_with_diff_displacement.items():
        dirname = 'x_{0:.3f}/z_0'.format(displace)
        gen_input.write_input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geometry, ele_to_bs_type, elements, functional, dirname, if_bs_change)
        submit_job.copy_submit_scr(path, dirname)

    #Generation of the INPUTs with different displacement and different layer distance
    for displace, geometry in geo_with_diff_displacement.items():
        Geo_with_diff_Dis_diff_Distance = gen_displacement_series.Range_of_Distances(geometry, fixed_atoms)
        geo_with_diff_dis_diff_distance = Geo_with_diff_Dis_diff_Distance.get_geo_series()
        distances = list(geo_with_diff_dis_diff_distance.keys())
        distances.sort()
        #Select the some of the distance values
        for key in list(geo_with_diff_dis_diff_distance.keys()):
            if key not in distances[1:5]:
                #print(key)
                del geo_with_diff_dis_diff_distance[key]
        #print(list(geo_with_diff_dis_diff_distance.keys()))
        for distance, geo in geo_with_diff_dis_diff_distance.items():
            dirname = 'x_{0:.3f}/z_{1:.3f}'.format(displace, distance)
            gen_input.write_input(path, name, slab_or_molecule, group, lattice_parameter, number_of_atoms, geo, ele_to_bs_type, elements, functional, dirname, if_bs_change)
            submit_job.copy_submit_scr(path, dirname)

    #Submit the calculation job
    job_dirs = submit_job.get_job_dirs(path)
    #submitted_path = submit_job.submit(job_dirs)

    #read calculation results
    #read_results.read_all_results(job_dirs, init_distance)

    read_results.write_init_distance(path, init_distance)
    print('Geometry optimization finished!!!')


def hf1(path):

    file = os.path.exists('INPUT')
    job_dirs = generation_of_input.get_job_dirs(path)

    #read basic computation infomation
    if file:
        hf1_bs_type = generation_of_input.read_inp(path)
        Gen_Input = generation_of_input.Gen_Inp(job_dirs[0])
        geometry = Gen_Input.get_geometry()
        #print(job_dirs)

        if hf1_bs_type == 'default':
            if_bs_change = 0

        else:
            if_bs_change = 1
            Bs_Init = Initialization.Bs_Init(geometry, bs_type=hf1_bs_type)
            ele_to_bs_type, elements = Bs_Init.gen_bs_info(if_bs_change)
    else:
        print('INPUT file does not exist!!!')
        print('''Do you want to start initialization or exit?
                 Please enter 1 to start initialization programm and enter 0 to exit the programm''')

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
    #submitted_path = submit_job.submit(job_dirs)

    #read calculation results
    read_results_hf1.read_all_results(job_dirs)
    read_results.write_init_distance(path, init_distance)

    print('Hartree Fock calculation 1 finished!!!')


def localization(path):

    job_dirs = Localization.copy_inp_loc.get_job_dirs(path)

    #copy input file of localiztion
    if len(job_dirs) != 0:
        Localization.copy_inp_loc.copy_all_files(job_dirs)
    else:
        print('There is no appropriate Hartree Fock calculation results!!! ')
        print('Programm will exit and correct the error and restart from localization step!!!')
        try:
            sys.exit(1)
        except:
            print('Program Exits.')
        finally:
            print('---------------------------------------------------------------------------------------')

    #copy job submit file to each directory
    Localization.submit_job_loc.copy_all_files(job_dirs)
    loc_job_dirs = Localization.submit_job_loc.get_job_dirs(path)
    #submitted_paths = Localization.submit_job_loc.submit(loc_job_dirs)

    #test finished
    while True:
        if Localization.submit_job_loc.test_all_loc_finished(loc_job_dirs):
            print ('Localization finished!')
            break
        else:
            time.sleep(500)
            continue


def hf2(path):

    file = os.path.exists('INPUT')
    job_dirs = HF2.generation_input_hf2.get_job_dirs(path)
    hf1_paths = []
    for job in job_dirs:
        job_path = Job_path(job)
        hf1_paths.append(job_path)

    #catagorization
    bilayer = []
    singlelayer = []
    for job_path in hf1_paths:
        if job_path.layertype == 'bilayer':
            bilayer.append(job_path)
        elif job_path.layertype == 'underlayer' or job_path.layertype == 'upperlayer':
            singlelayer.append(job_path)

    #read basic computation infomation
    if file:
        pass
    else:
        print('INPUT file does not exist!!!')
        print('''Do you want to start initialization or exit?
                 Please enter 1 to start initialization programm and enter 0 to exit the programm''')

    #generation of all input files
    for job in bilayer:
        Inp = HF2.generation_input_hf2.Input(job)
        Inp.gen_input()
    for job in singlelayer:
        Inp = HF2.inp_layers_hf2.Layer_Inp(job)
        Inp.gen_input()

    #submit the jobs
    hf2_job_dirs = bilayer + singlelayer
    #submitted_path = HF2.submit_job_hf2.submit(hf2_job_dirs)

    #read calculation results
    #read_results_hf1.read_all_results(job_dirs)
    #read_results.write_init_distance(path, init_distance)

    print('Hartree Fock calculation 2 optimization finished!!!')


def pipeline(path):
    #geo_opt(path)
    #hf1(path)
    #localization(path)
    hf2(path)
