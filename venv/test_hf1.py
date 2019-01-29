#!/usr/bin/python3
import os
from Common import  Job_path
from HF1 import select_jobs
from HF1 import Input
from HF1 import Layer_Inp
from HF1 import read_all_results_hf1
from HF1 import if_cal_finish

def test_select_jobs():
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    jobs = select_jobs(path)
    print(path)
    print(jobs)

def test_Input():
    path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\Test\\geo_opt\\x_0\\z_0.979'
    job = Job_path(path)
    Inp = Input(job, 'blackP', 'SLAB', '1', 'default')
    Inp.gen_input()

def test_Layer_Inp():
    path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\Test\\geo_opt\\x_0\\z_0.979'
    job = Job_path(path)
    Inp = Layer_Inp(job, 'blackP', 'SLAB', '1', 'default', layertype='upperlayer')
    Inp.gen_input()

def test_if_finished():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_1\x_-0.150\z_-0.106'
    job = Job_path(path)
    res = if_cal_finish(job)
    print(res)

def test_read_all_results():
    path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\hf_1'
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'hf.out' in files:
            job = Job_path(root)
            if if_cal_finish(job):
                jobs.append(job)
    read_all_results_hf1(jobs, init_dist=3.1)

def test_suite():
    #test_select_jobs()
    #test_Input()
    #test_Layer_Inp()
    test_read_all_results()
    #test_if_finished()


test_suite()
