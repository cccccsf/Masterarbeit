#!/usr/bin/python3
import os
import sys
import Initialization
from copy import deepcopy
from read_input import Read_input
from Crystal import Geometry
import geometry_optimization
from Common import mkdir
from Common import Job_path
from Common import record
from Common import ReadIni
from Common import look_for_in_list
# from HF1 import generation_of_input
# from HF1 import input_of_layers
# from HF1 import submit_job_hf1
# from HF1 import read_results_hf1
# from HF1.read_results_hf1 import get_x_z_and_layertype
# import Localization
# import HF2
# import LMP2
# import RPA


def geo_opt(path):

    mkdir(path)
    rec = 'Geometry Optimization begins...'
    print(rec)
    record(path, rec)
    geometry_optimization.creat_geo_lat_json(path)

    ini_path = os.path.dirname(__file__)
    file = os.path.join(ini_path, 'input.ini')
    file = os.path.exists(file)

    if file:
        Ini = ReadIni(ini_path)
        name, slab_or_molecule, group, lattice_parameter, number_of_atoms, fixed_atoms = Ini.get_basic_info()
        geometry = Ini.get_geometry()
        if type(fixed_atoms) == list and len(fixed_atoms) == 2:
            geometry = Geometry(geometry = geometry, fixed_atoms=fixed_atoms)
        else:
            geometry = Geometry(geometry = geometry)
        original_geometry = deepcopy(geometry)
        bs_type, functional, nodes = Ini.get_geo_opt_info()

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

    jobs = []

    #generation of the first INPUT
    dirname = 'x_0/z_0'
    job = os.path.join(path, 'geo_opt')
    job = os.path.join(job, dirname)
    job = Job_path(job)
    Geo_Inp = geometry_optimization.Geo_Opt_Input(job, name, slab_or_molecule, group, lattice_parameter, geometry, bs_type, functional)
    Geo_Inp.gen_input()
    jobs.append(job)
    geometry_optimization.write_init_dist(geometry, path)


    job_geo_dict = {}
    #Generation of the job with different layer distance
    diff_distances = geometry_optimization.Range_of_Distances(geometry, job)
    geo_with_diff_distance = diff_distances.get_geo_series()
    init_distance = diff_distances.init_distance


    for distance, geometry in geo_with_diff_distance.items():
        new_job = deepcopy(job)
        new_z_dirname = 'z_{0:.3f}'.format(distance)
        new_job.reset('z_dirname', new_z_dirname)
        job_geo_dict[new_job] = geometry


    #Generation of the job with different displacement, produce ((0.1, 0), (0.25, 0), (0.35, 0), (0.5, 0))
    range_of_displacement = geometry_optimization.Range_of_Displacement(original_geometry, job)
    geo_with_diff_displacement = range_of_displacement.get_geo_series()
    job_geo_dict_dis = {}

    for displacement, geometry in geo_with_diff_displacement.items():
        new_job = deepcopy(job)
        new_x_dirname = 'x_{0:.2f}'.format(displacement)
        new_job.reset('x_dirname', new_x_dirname)
        job_geo_dict_dis[new_job] = geometry
        job_geo_dict[new_job] = geometry

    #generation all INPUT files besides the first one above
    for job, geometry in job_geo_dict.items():
        Geo_Inp = geometry_optimization.Geo_Opt_Input(job, name, slab_or_molecule, group, lattice_parameter, geometry, bs_type, functional)
        Geo_Inp.gen_input()
        jobs.append(job)
    #Copy files and Submit the calculation job above
    # jobs_finished = geometry_optimization.submit(jobs, nodes)


    #Select the optimal distance of each x point
    para = [name, slab_or_molecule, group, lattice_parameter, bs_type, functional, nodes]
    #x_10
    x_10 = {job: geometry for job, geometry in job_geo_dict_dis.items() if job.x == '0.10'}
    jobs_10 = [job for job in job_geo_dict_dis.keys() if job.x == '0.10']
    init_job_10 = jobs_10[0]
    jobs_10, x_10, min_job_10, jobs_10_finished = geometry_optimization.select_optimal_dist(x_10, 0, para)
    jobs += jobs_10
    # New_Geo_10 = geometry_optimization.Select_Opt_Dis(x_10[init_job_10], init_job_10)
    # new_geo_10 = New_Geo_10.get_geo_series()
    # new_geo_10_dict = {}
    # for distance, geometry in new_geo_10.items():
    #     print(distance)
    #     new_job = deepcopy(list(x_10.keys())[0])
    #     new_z_dirname = 'z_{0:.3f}'.format(distance)
    #     new_job.reset('z_dirname', new_z_dirname)
    #     new_geo_10_dict[new_job] = geometry
    #     x_10[new_job] = geometry
    # for job, geometry in new_geo_10_dict.items():
    #     Geo_Inp = geometry_optimization.Geo_Opt_Input(job, name, slab_or_molecule, group, lattice_parameter, geometry, bs_type, functional)
    #     Geo_Inp.gen_input()
    #     jobs.append(job)
    #     jobs_10.append(job)
    # #jobs_10_finished = geometry_optimization.submit(new_jobs, nodes)
    # # jobs_finished += jobs_10_finished
    # min_dist_10, min_job_10 = geometry_optimization.read_and_select_lowest_e(jobs_10)
    # while True:
    #     jobs_10 = sorted(jobs_10, key=lambda job: float(job.z))
    #     point = look_for_in_list(jobs_10, min_job_10)
    #     if (len(jobs_10) - point) == 1:
    #         New_Geo_10 = geometry_optimization.Select_Opt_Dis(x_10[min_job_10], min_job_10, direct=2)
    #         new_geo_10 = New_Geo_10.get_geo_series()
    #     if (len(jobs_10) - point) == 2:
    #         New_Geo_10 = geometry_optimization.Select_Opt_Dis(x_10[min_job_10], min_job_10, direct=3)
    #         new_geo_10 = New_Geo_10.get_geo_series()
    #     if (len(jobs_10) - point) >= 3:
    #         if len(jobs_10) >= 4:
    #             break
    #         else:
    #             New_Geo_10 = geometry_optimization.Select_Opt_Dis(x_10[min_job_10], min_job_10, direct=-2)
    #             new_geo_10 = New_Geo_10.get_geo_series()
    #     new_geo_10_dict = {}
    #     for distance, geometry in new_geo_10.items():
    #         new_dist = distance + min_dist_10
    #         new_z_dirname = 'z_{0:.3f}'.format(new_dist)
    #         old_z_dirmane = min_job_10.z_dirname
    #         new_path = min_job_10.path.replace(old_z_dirmane, new_z_dirname)
    #         new_job = Job_path(new_path)
    #         new_geo_10_dict[new_job] = geometry
    #         x_10[new_job] = geometry
    #         dist_list_10.append(new_dist)
    #     new_jobs = []
    #     for job, geometry in new_geo_10_dict.items():
    #         Geo_Inp = geometry_optimization.Geo_Opt_Input(job, name, slab_or_molecule, group, lattice_parameter, geometry, bs_type, functional)
    #         #Geo_Inp.gen_input()
    #         jobs.append(job)
    #         jobs_10.append(job)
    #         new_jobs.append(job)
    #         #jobs_10_finished = geometry_optimization.submit(new_jobs, nodes)
    #     min_dist_10, min_job_10 = geometry_optimization.read_and_select_lowest_e(jobs_10)
    #x_25
    x_25 = {job: geometry for job, geometry in job_geo_dict_dis.items() if job.x == '0.25'}
    jobs_25 = [job for job in job_geo_dict_dis.keys() if job.x == '0.25']
    init_job_25 = jobs_25[0]
    pos_min_10 = look_for_in_list(jobs_10, min_job_10)
    pos_init_10 = look_for_in_list(jobs_10, init_job_10)
    diff = pos_min_10 - pos_init_10
    jobs_25, x_25, min_job_25, jobs_25_finished = geometry_optimization.select_optimal_dist(x_25, diff)
    jobs += jobs_25
    #x_35
    x_35 = {job: geometry for job, geometry in job_geo_dict_dis.items() if job.x == '0.35'}
    init_job_35 = list(x_35.keys())[0]
    pos_min_25 = look_for_in_list(jobs_25, min_job_25)
    pos_init_25 = look_for_in_list(jobs_25, init_job_25)
    diff = pos_min_25 - pos_init_25
    jobs_35, x_35, min_job_35, jobs_35_finished = geometry_optimization.select_optimal_dist(x_35, diff)
    jobs += jobs_35
    #x_50
    x_50 = {job: geometry for job, geometry in job_geo_dict_dis.items() if job.x == '0.50'}
    init_job_50 = list(x_50.keys())[0]
    pos_min_35 = look_for_in_list(jobs_35, min_job_35)
    pos_init_35 = look_for_in_list(jobs_35, init_job_35)
    diff = pos_min_35 - pos_init_35
    jobs_50, x_50, min_job_50, jobs_50_finished = geometry_optimization.select_optimal_dist(x_50, diff)
    jobs += jobs_50

    #read calculation results
    # jobs_finished += jobs_10_finished
    # jobs_finished += jobs_25_finished
    # jobs_finished += jobs_35_finished
    # jobs_finished += jobs_50_finished
    # geometry_optimization.read_all_results(jobs_finished, init_distance)

    print('Geometry optimization finished!!!')
    record(path, 'Geometry optimization finished!!!')


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
    #submitted_jobs_hf1 = submit_job.submit(job_dirs)

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
        HF2.submit_job_hf2.copy_submit_scr(job)
        HF2.submit_job_hf2.copy_fort9(job)
    for job in singlelayer:
        Inp = HF2.inp_layers_hf2.Layer_Inp(job)
        Inp.gen_input()
        HF2.submit_job_hf2.copy_submit_scr(job)
        HF2.submit_job_hf2.copy_fort9(job)

    #submit the jobs
    hf2_job_dirs = bilayer + singlelayer
    for i in range(len(hf2_job_dirss)):
        hf2_job_dirs[i].reset('method', 'hf_2')
    #submitted_jobs_hf2 = HF2.submit_job_hf2.submit(hf2_job_dirs)

    #read calculation results
    #HF2.read_all_results(submitted_jobs_hf2)

    print('Hartree Fock calculation 2 finished!!!')


def lmp2(path):

    job_paths = LMP2.get_jobs(path)
    hf2_jobs = []
    for p in job_paths:
        job = Job_path(p)
        hf2_jobs.append(job)

    #catagorization
    bilayer = []
    singlelayer = []
    for job in hf2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    #read basic computation infomation
    file = os.path.exists('INPUT')
    if file:
        pass
    # else:
    #
    #     print('INPUT file does not exist!!!')
    #     print('''Do you want to start initialization or exit?
    #              Please enter 1 to start initialization programm and enter 0 to exit the programm''')

    #generation of all input files and copy needed files
    for job in bilayer:
        Inp = LMP2.Lmp2_Input(job)
        Inp.write_input()
        LMP2.copy_files(job)
    for job in singlelayer:
        Inp = LMP2.Lmp2_Input_Layer(job)
        Inp.write_input()
        LMP2.copy_files(job)

    #submit the jobs
    lmp2_jobs = bilayer + singlelayer
    for i in range(len(lmp2_jobs)):
        lmp2_jobs[i].reset('method', 'lmp2')
    #finished_jobs_lmp2 = LMP2.submit(lmp2_jobs)

    #read calculation results
    #LMP2.read_all_results(finished_jobs_lmp2)

    print('LMP2 calculation finished!!!')



def rpa(path):

    jobs = RPA.get_jobs(path)
    lmp2_jobs = []
    for p in jobs:
        job = Job_path(p)
        lmp2_jobs.append(job)

    #catagorization
    bilayer = []
    singlelayer = []
    for job in lmp2_jobs:
        if job.layertype == 'bilayer':
            bilayer.append(job)
        elif job.layertype == 'underlayer' or job.layertype == 'upperlayer':
            singlelayer.append(job)

    #generation of all input files
    for job in bilayer:
        Inp = RPA.RPA_Input(job, '12000')
        Inp.generate_input()
    for job in singlelayer:
        Inp = RPA.RPA_Input(job, '2900')
        Inp.generate_input()

    #copy files and submit the jobs
    rpa_jobs = bilayer + singlelayer
    for i in range(len(rpa_jobs)):
        rpa_jobs[i].reset('method', 'rpa')
    for job in rpa_jobs:
        RPA.copy_submit_src(job)
    #finished_jobs_rpa = RPA.submit(lmp2_jobs)

    #read calculation results
    #RPA.read_all_results(finished_jobs_rpa)

    print('LRPA calculation finished!!!')


def pipeline(path, start):
    geo_opt(path)
    #hf1(path)
    #localization(path)
    #hf2(path)
    #lmp2(path)
    #rpa(path)
