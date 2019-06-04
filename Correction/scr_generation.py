#!/usr/bin/python3
import os


class Script(object):

    def __init__(self, job, molpro_key, molpro_path):
        self.job = job
        self.path = job.path
        self.job_type = job.method
        self.scr_file = os.path.join(self.path, self.job_type)

        self.nodes = job.parameter['node']
        self.molpro_key = molpro_key
        self.molpro_path = molpro_path

    def write_beginning(self):
        with open(self.scr_file, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('#PBS -j eo\n')
            f.write('#PBS -r n\n')
            f.write('#PBS -l nodes={}\n'.format(self.nodes))
            f.write('\n')

    def write_vairabes(self):
        with open(self.scr_file, 'a') as f:
            f.write('module load XE2016.0.3.210\n')
            f.write('export MOLPRO_KEY={}\n'.format(self.molpro_key))
            molpro_path = self.deal_with_mopro_path()
            f.write('export PATH=.:{}:${{PATH}}\n'.format(molpro_path))
            f.write('\n')

    def deal_with_mopro_path(self):
        path = os.path.split(self.molpro_path)
        if path[-1] == '':
            path = os.path.split(path[0])
        if path[0].endswith('Molpro') and path[-1] == 'bin':
            root = path[0]
            lib_path = os.path.join(root, 'lib')
            bin_path = self.molpro_path
        elif path[0].endswith('Molpro') and path[-1] == 'lib':
            root = path[0]
            lib_path = self.molpro_path
            bin_path = os.path.join(root, 'bin')
        elif path[-1] == 'Molpro':
            root = self.molpro_path
            lib_path = os.path.join(root, 'lib')
            bin_path = os.path.join(root, 'bin')
        molpro_path = '{}:{}'.format(bin_path, lib_path)
        return molpro_path

    def write_run_step(self):
        inp_file = self.job_type + '.inp'
        with open(self.scr_file, 'a') as f:
            f.write('currdir=/scratch/$USER/$$tmp\n')
            f.write('mkdir -p $currdir\n')
            f.write('cd ${PBS_O_WORKDIR}\n')
            f.write('\n')
            f.write('molpro -n {} {} -d $currdir -I $currdir -W $currdir\n'.format(self.nodes, inp_file))
            f.write('\n')
            f.write('rm -r $currdir\n')

    def write_scr(self):
        self.write_beginning()
        self.write_vairabes()
        self.write_run_step()
