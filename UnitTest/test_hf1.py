#!/usr/bin/python3
import os
from Common import  Job
from HF1 import select_jobs
from HF1 import Input
from HF1 import Layer_Inp
from HF1 import read_all_results_hf1
from HF1 import if_cal_finish
import HF1

def test_select_jobs():
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    jobs = select_jobs(path)
    print(path)
    print(jobs)

def test_Input():
    path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\Test\\geo_opt\\x_0\\z_0.979'
    job = Job(path)
    Inp = Input(job, 'blackP', 'SLAB', '1', 'default')
    Inp.gen_input()

def test_Layer_Inp():
    path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\Test\\geo_opt\\x_0\\z_0.979'
    job = Job(path)
    Inp = Layer_Inp(job, 'blackP', 'SLAB', '1', 'default', layertype='upperlayer')
    Inp.gen_input()

def test_if_finished():
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\hf_1\x_-0.150\z_-0.106'
    job = Job(path)
    res = if_cal_finish(job)
    print(res)

def test_read_all_results():
    path = 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\hf_1'
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'hf.out' in files:
            job = Job(root)
            if if_cal_finish(job):
                jobs.append(job)
    read_all_results_hf1(jobs, init_dist=3.1)

def test_too_many_cycles():
    job = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\hf1\x_0.35\z_0'
    job2 = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\hf1\x_0.35\z_0\underlayer'
    job = Job(job)
    e = HF1.read_results_hf1.get_energy(job.path)
    print(e)
    print('---'*20)
    e1 = HF1.read_results_hf1.get_energy(job2)
    print(e1)

def test_delete_guessp():
    job = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\hf1\x_0.35\z_0'
    job2 = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\hf1\x_0.35\z_0\underlayer'
    job = Job(job)
    HF1.delete_guessp(job)


def test_suite():
    #test_select_jobs()
    #test_Input()
    #test_Layer_Inp()
    #test_read_all_results()
    #test_if_finished()
    #test_too_many_cycles()
    #test_delete_guessp()
    pass


test_suite()
