#!/usr/bin/python3
import os

def delete_guessp(job):
    path = job.path
    file = os.path.join(path, 'INPUT')
    if os.path.exists(file):
        with open(file) as f:
            lines = f.readlines()
            guessp = 'GUESSP\n'
            lines = [line for line in lines if line != guessp]
        with open(file, 'w') as f:
            f.writelines(lines)
    else:
        print('No INPUT file exits...')
