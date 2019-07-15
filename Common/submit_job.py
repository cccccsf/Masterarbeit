#!/usr/bin/python3
import os
import subprocess


def submit_job(job, method=''):
    """
    submit job to PBS system
    :param job: Components.Job
    :param method: name of submit file
    :return:
    """
    path = job.path
    if method == '':
        method = job.method
    os.chdir(path)
    try:
        chmod = 'chmod u+x {}'.format(method)
        subprocess.call(chmod, shell=True)
        out_bytes = subprocess.check_output(['qsub', method])
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        print(code)
    except FileNotFoundError as e:
        print(e)
        print('Windows Test.')
        out_text = '*****.rigi'
        return out_text
    out_text = out_bytes.decode('utf-8')
    out_text = out_text.strip('\n')
    return out_text
