#!/usr/bin/python3
import os
import re
import shutil
import subprocess
from copy import  deepcopy
from Common import mkdir
from Common import Job
from LMP2.submit_job_lmp2 import if_cal_finish


def get_jobs(path):
    path = os.path.join(path, 'hf_2')
    walks = os.walk(path)
    jobs = []
    for root, dirs, files in walks:
        if 'lmp2.out' in files and 'molpro.inp' in files:
            new_job = Job(root)
            if if_cal_finish(new_job):
                jobs.append(new_job)
    return jobs


class RPA_Input(object):

    def __init__(self, job, memory='12000'):
        self.lmp2_job = job
        self.rpa_job = 0
        self.rpa_path = ''
        self.get_new_job()

        self.memory = memory


    def get_new_job(self):
        self.rpa_job = deepcopy(self.lmp2_job)
        self.rpa_job.reset('method', 'rpa')
        self.rpa_path = self.rpa_job.path


    def copy_molpro_inp(self):
        mkdir(self.rpa_path)
        inp_from = self.lmp2_job.path
        inp_from = os.path.join(inp_from, 'molpro.inp')
        inp_to = os.path.join(self.rpa_path, 'rpa.inp')
        shutil.copy(inp_from, inp_to)


    def change_form_molpro_inp(self):
        # only for shell, not windows
        # os.chdir(path)
        # com_memory = 'sed -i -e \'s/1536/{}/g\' rpa.inp'.format(memory)
        #subprocess.call(com_memory, shell=True)
        file_path = os.path.join(self.rpa_path, 'rpa.inp')
        with open(file_path, 'r') as f:
            molpro_inp = f.read()
        memory_formal = '1536'
        try:
            line0 = re.search('memory.*?\n', molpro_inp).group(0)
            line0 = line0.split(',')
            memory_formal = line0[1]
        except Exception as e:
            print(e)
            print('Fail to read formal memory size')
        molpro_inp = re.sub('{}'.format(memory_formal), '{}'.format(self.memory), molpro_inp, count=1)
        molpro_inp = re.sub('P\s+', 'p', molpro_inp)
        with open(file_path, 'w') as f:
            f.write(molpro_inp)


    def generate_input(self):
        self.copy_molpro_inp()
        self.change_form_molpro_inp()
