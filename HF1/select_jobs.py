#!/usr/bin/python3
import os
from Common import Job
from Common import look_for_in_list
from GeoOPt import read_and_select_lowest_e


def select_jobs(path):

    # find all possible jobs
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'geo_opt.out' in files:
            jobs.append(root)
    jobs = [Job(job) for job in jobs]


    # catagorization jobs according to x
    jobs_dict = {}
    for job in jobs:
        x = job.x
        if x in jobs_dict:
            jobs_dict[x].append(job)
        else:
            jobs_dict[x] = [job]

    #select jobs at each x
    selected_jobs = []
    for key, value in jobs_dict.items():
        if key == '0':
            new_list = value
        else:
            jobs_list = value[:]
            min_dist, min_job = read_and_select_lowest_e(value)
            jobs_list = sorted(jobs_list, key=lambda job: float(job.z))
            length = len(jobs_list)
            position = look_for_in_list(jobs_list, min_job)
            if len(jobs_list) >3:
                new_list = [min_job]
                new_list.append(jobs_list[-1])
                new_list.append(jobs_list[-2])
                new_list.append(jobs_list[0])
            else:
                new_list = [job for job in jobs_list]
        selected_jobs += new_list

    return selected_jobs
