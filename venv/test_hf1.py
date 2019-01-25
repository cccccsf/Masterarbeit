#!/usr/bin/python3
import os
from Common import  Job_path
from HF1 import select_jobs
from HF1 import Input

def test_select_jobs():
    path = os.path.dirname(__file__)
    path = os.path.dirname(path)
    select_jobs(path)

def test_Input():
    path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\Test\\geo_opt\\x_0\\z_0.979'
    job = Job_path(path)
    Inp = Input(job, 'blackP', 'SLAB', '1', 'default', [])
    Inp.gen_input()


def test_suite():
    #test_select_jobs()
    test_Input()


test_suite()
