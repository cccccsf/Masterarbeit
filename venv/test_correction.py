#!/usr/bin/python3
import os
import Correction
from Correction import correction
from Common import Job_path



def test_get_jobs():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test'
    jobs = correction.get_jobs(path)
    print(jobs)

def test_check_com_file():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster'
    res = check_inp_file(path)
    expected = True
    assert expected == res

def test_Molpro_Bs():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster\x_0\z_0'
    job = Job_path(path)
    xyz = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster\x_0\z_0\BlackP_Cluster_M.xyz'
    inp_name = 'per_bas_rpa_iext1.inp'
    MB = Correction.Molpro_Bs(job, inp_name)
    MB.get_molpro_bs()
    MB.write_bs()

def test_if_cal_finish():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster\x_0\z_0'
    job = Job_path(path)
    job.method = 'avdz_rpa_cc'
    finished = Correction.if_cal_finish(job)

def test_read_results():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster\x_0\z_0'
    job = Job_path(path)
    job.method = 'avtz_iext1_rpa'
    Res = Correction.Result(job)
    Res.get_energy()
    print(Res.energy, Res.unit)
    Res.unit_transform()
    print(Res.energy, Res.unit)



def test_suite():
    #test_get_jobs()
    #test_check_com_file()
    #test_Molpro_Bs()
    #test_if_cal_finish()
    test_read_results()
    pass

test_suite()
