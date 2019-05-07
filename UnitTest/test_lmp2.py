#!/usr/bin/python3
import os
from LMP2 import input
from LMP2 import submit_job_lmp2
from LMP2 import read_results_lmp2
from Common.job import Job
from Common import ReadIni


def test_Input():
    path = os.getcwd()
    path = path + '/Test/hf_2/x_-0.150/z_-0.106'
    job = Job(path)
    inp = input.Lmp2_Input(job)
    inp.write_input()

def test_get_jobs(path):
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test'
    jobs = input.get_jobs(path)
    expected = ['C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\hf_2\\x_-0.150\\z_-0.106', 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\hf_2\\x_-0.150\\z_-0.106\\underlayer', 'C:\\Users\\ccccc\\Documents\\Theoritische Chemie\\Masterarbeit\\test\\hf_2\\x_-0.150\\z_-0.106\\upperlayer']
    #expected = ['/users/shch/project/Layer_Structure_Caculation/venv/Test/hf_2/x_-0.150/z_-0.106', '/users/shch/project/Layer_Structure_Caculation/venv/Test/hf_2/x_-0.150/z_-0.106/underlayer', '/users/shch/project/Layer_Structure_Caculation/venv/Test/hf_2/x_-0.150/z_-0.106/upperlayer']
    # assert(jobs == expected)


def test_Input_Layer():
    path = os.getcwd()
    path = path + '/Test/hf_2/x_-0.150/z_-0.106/upperlayer'
    job = Job(path)
    inp = input.Lmp2_Input_Layer(job)
    inp.write_input()


def test_if_finished():
    path = os.getcwd()
    path = path + '/Test/lmp2/x_-0.150/z_-0.106'
    job = Job(path)
    if_finish = submit_job_lmp2.if_cal_finish(job)
    expected = True
    assert(expected == if_finish)


def test_get_energy():
    path = os.getcwd()
    path = path + '/Test/lmp2/x_-0.150/z_-0.106'
    lmp2, scs = read_results_lmp2.get_energy(path)
    lmp2_expected = '-0.1308098696E+01'
    scs_expected = '-0.1237122416E+01'

def test_read_all_results():
    path = os.getcwd()
    path = path + '/Test/lmp2/x_-0.150/z_-0.106'
    paths = []
    paths.append(path)
    paths.append(path + '/underlayer')
    paths.append(path + '/upperlayer')
    jobs = []
    for p in paths:
        job = Job(p)
        jobs.append(job)
    read_results_lmp2.read_all_results(jobs)

def test_update_scr():
    ini = os.path.dirname(__file__)
    Ini = ReadIni(ini)
    nodes, cryscor = Ini.get_lmp2_info()
    path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\test\lmp2\x_-0.150\z_-0.106'
    job = Job(path)
    submit_job_lmp2.update_scr(job, nodes, cryscor)



def test_suite():
    # path = os.path.realpath(__file__)
    # path = os.path.dirname(path)
    # path = os.path.join(path, 'Test')
    # test_get_jobs(path)
    # #test_Input()
    # #test_Input_Layer()
    # test_if_finished()
    # test_get_energy()
    # test_read_all_results()
    test_update_scr()

test_suite()
