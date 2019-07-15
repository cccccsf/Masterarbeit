#!/usr/bin/python3
import os
import subprocess


class Monitor(object):

    def __init__(self, path):
        self.path = path
        self.jobs = []

    def get_curr_status(self):
        command = 'qstat'
        try:
            out = subprocess.check_output([command, '-n'])
        except subprocess.CalledProcessError as e:
            out = e.output
            code = e.returncode
            print(code)
        out_text = out.decode('utf-8')
        return out_text

    def record_status(self, status):
        status_file = os.path.join(self.path, 'jobs_status.json')
        with open(status_file, 'w') as f:
            f.write(status)


if __name__ == '__main__':
    path = r'/users/shch/project/Masterarbeit/Test'
    mo = Monitor(path)
    out = mo.get_curr_status()
    mo.record_status(out)
