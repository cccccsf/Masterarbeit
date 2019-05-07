#!/usr/bin/python3
import Results
from Common import Job

def test_get_jobs():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test'
    jobs = Results.get_jobs(path)

def test_pipeline():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test'
    Results.results(path)

def test_CorrectionResults():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster\x_2.5\d_int_3.70'
    job = Job(path)
    job.method = 'avtz_rpa_cc'
    CR = Results.CorrectionResult(job)
    CR.read_energy()

def test_FResult():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\hf2\x_2.5\d_int_3.70'
    job = Job(path)
    FR = Results.FResult(job)
    FR.read_info_from_json()



def test_suite():
    #test_get_jobs()
    test_pipeline()
    #test_CorrectionResults()
    #test_FResult()
    pass

test_suite()
