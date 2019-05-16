#!/usr/bin/python3
import os


def if_cluster_already_generated(job):
    path = job.path
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.xyz'):
                return True
    return False
