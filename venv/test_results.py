#!/usr/bin/python3
import Results
from Common import Job_path

def test_get_jobs():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test'
    jobs = Results.get_jobs(path)

def test_pipeline():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test'
    Results.results(path)

def test_CorrectionResults():
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\cluster\x_2.5\d_int_3.70'
    job = Job_path(path)
    job.method = 'avtz_rpa_cc'
    CR = Results.CorrectionResult(job)
    CR.read_energy()



def test_suite():
    #test_get_jobs()
    test_pipeline()
    #test_CorrectionResults()
    pass

test_suite()
