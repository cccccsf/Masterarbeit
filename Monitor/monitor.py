#!/usr/bin/python3
import os
import json
import subprocess


class Monitor(object):

    def __init__(self, path):
        self.path = path
        self.curr_jobs = {}
        self.finished_jobs = []
        self.status_file = os.path.join(self.path, 'jobs_status.json')
        self.curr_status = ''
        self.creat_json_file()

    def qstat_n(self):
        command = 'qstat'
        try:
            out = subprocess.check_output([command, '-n'])
            out_text = out.decode('utf-8')
        except subprocess.CalledProcessError as e:
            out = e.output
            code = e.returncode
            print(code)
            out_text = out.decode('utf-8')
        except FileNotFoundError as e:
            print(e)
            print('Windows Test.')
            out_text = ''
        return out_text

    def record_status(self, status):
        with open(self.status_file, 'w') as f:
            f.write(status)

    def get_qstatn_info(self, job_id, out=''):
        if out == '':
            s = self.status_file.replace('jobs_status', 'status')
            with open(s, 'r') as f:
                infos = f.readlines()
        else:
            infos = out.split('\n')
        loc = 0
        for i in range(len(infos)):
            if infos[i].startswith(job_id):
                loc = i
        if loc > 0:
            status = infos[loc]
            status = status.split()
            status = status[-3]
            node = infos[loc+1]
            node = node.split('/')
            node = node[0].strip()
        else:
            status = 'T'
            node = 0
        return status, node

    def update_status(self):
        self.curr_status = self.qstat_n()
        del_jobs = []
        for job, id in self.curr_jobs.items():
            status, node = self.get_qstatn_info(id, self.curr_status)
            self.update_json(job, 'node', node)
            if status == 'T':
                self.finished_jobs.append(job)
                del_jobs.append(job)
                self.update_json(job, 'status', 'terminated')
            elif status == 'R':
                self.update_json(job, 'status', 'running')
            elif status == 'Q':
                self.update_json(job, 'status', 'waiting')
        for job in del_jobs:
            del self.curr_jobs[job]

    def insert_new_job(self, job, id):
        self.curr_jobs[job] = id
        self.update_json(job, 'id', id)
        self.update_json(job, 'status', 'submitted')

    def update_json(self, job, key, value):
        coord = '{}'.format(job.coord)
        job_name = str(job)
        with open(self.status_file, 'r') as f:
            data = json.load(f)
        if job_name not in data:
            data[job_name] = {}
            data[job_name]['method'] = job.method
            data[job_name]['path'] = job.path
        data[job_name][key] = value
        with open(self.status_file, 'w') as f:
            json.dump(data, f, indent=4)

    def creat_json_file(self):
        if not os.path.exists(self.status_file):
            data = {}
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=4)


if __name__ == '__main__':
    # path = r'/users/shch/project/Masterarbeit/Test'
    path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\test_may'
    mo = Monitor(path)
    # out = mo.qstat_n()
    # mo.record_status(out)
    job_id = '87919.rigi'
    mo.get_qstatn_info(job_id)
