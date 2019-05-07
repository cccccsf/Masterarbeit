#!/usr/bin/python3
import os
from RPA import RPA_Input
from RPA import submit_job_rpa
from RPA import copy_submit_src
from RPA import read_results_rpa
from Common import Job



def test_rpa_input():
    path = os.getcwd()
    path = path + '/Test/lmp2/x_-0.150/z_-0.106'
    job = Job(path)
    inp = RPA_Input(job)
    inp.generate_input()

def test_copy_job():
    path = os.getcwd()
    path = path + '/Test/rpa/x_-0.150/z_-0.106'
    job = Job(path)
    copy_submit_src(job)

def test_if_finished():
    path = os.getcwd()
    path = path + '/Test/rpa/x_-0.150/z_-0.106'
    job = Job(path)
    finished = submit_job_rpa.if_cal_finish(job)
    expected = True
    assert(finished == expected)

def test_get_energy():
    path = os.getcwd()
    path = path + '/Test/rpa/x_-0.150/z_-0.106'
    e = read_results_rpa.get_energy(path)
    expected = '-0.950588132848'
    assert(expected == e)

def test_read_all_results():
    path = os.getcwd()
    path  = os.path.join(path, 'Test')
    path = os.path.join(path, 'rpa')
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'rpa.out' in files:
            job = Job(root)
            jobs.append(job)
    read_results_rpa.read_and_record_all_results(jobs)


def test_suite():
    #test_rpa_input()
    #test_copy_job()
    #test_if_finished()
    #test_get_energy()
    test_read_all_results()

test_suite()
