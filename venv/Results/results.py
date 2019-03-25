#!/usr/bin/python3
import os
from Correction import if_cal_finish


def results(path):

    # get jobs
    jobs = get_jobs(path)





def get_jobs(path):
    path = os.path.join(path, 'cluster')
    walks = os.walk(path)
    jobs = []
    path_set = set()
    for root, dirs, files in walks:
        if len(files) > 0:
            for file in files:
                
