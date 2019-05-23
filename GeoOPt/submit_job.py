#!/usr/bin/python3
import os
import re
import shutil
import time
import GeoOPt
from Common import record
from Common import Job
from Common import look_for_in_list
from Common import rename_file
from Common import submit_job


def update_nodes(path, nodes, crystal_path):
    scr = os.path.join(path, 'geo_opt')
    with open(scr, 'r') as f:
        lines = f.readlines()
    nodes_line = lines[3]
    loc = 3
    if nodes_line.startswith('#PBS -l nodes'):
        pass
    else:
        i = 0
        for line in lines:
            if line.startswith('#PBS -l nodes'):
                loc = i
            i += 1
    loc2, loc_cry = 0, 0
    j = 0
    for line in lines:
        if line.startswith('mpirun -np'):
            loc2 = j
        if line.startswith('crystal_path='):
            loc_cry = j
        j += 1
    if nodes != '':
        nodes_line = '#PBS -l nodes={}\n'.format(nodes)
        lines[loc] = nodes_line
        lines[loc2] = 'mpirun -np {} $crystal_path/Pcrystal >& ${{PBS_O_WORKDIR}}/geo_opt.out\n'.format(nodes)
    if crystal_path != '':
        lines[loc_cry] = 'crystal_path={}\n'.format(crystal_path)

    with open(scr, 'w') as f:
        f.writelines(lines)


def copy_fort9(job):
    ziel_path = job.path
    z_dirname = job.z_dirname
    x_dirname = job.x_dirname
    fort9_path = ziel_path.replace(z_dirname, 'z_0')
    fort9_path = fort9_path.replace(x_dirname, 'x_0')
    fort9_from = os.path.join(fort9_path, 'fort.9')
    fort9_to = os.path.join(ziel_path, 'fort.20')
    try:
        shutil.copy(fort9_from, fort9_to)
        print('fort.9 file copied...')
    except Exception as e:
        print(e)
        print('fort.9 failed to copy...')


def copy_submit_scr(job, nodes, crystal_path):
    ziel_path = job.path
    scr_path = os.path.dirname(os.path.realpath(__file__))
    if job.x == '0' and job.z == '0':
        scr_from = os.path.join(scr_path, 'job_submit.bash')
    else:
        scr_from = os.path.join(scr_path, 'job_submit_nonini.bash')
    scr_to = os.path.join(ziel_path, 'geo_opt')
    shutil.copy(scr_from, scr_to)
    update_nodes(ziel_path, nodes, crystal_path)
    print('Submition file copied...')


def if_cal_finish(job):
    """
    check the calculation is finished or not through the output file
    :param job: Common.Job
    :return: Bool True of False
    """
    path = job.path
    out_file = os.path.join(path, 'geo_opt.out')
    if not os.path.exists(out_file):
        return False
    else:
        file = open(out_file, 'r')
        lines = file.read().replace('\n', ':')
        lines = ' '.join(lines.split()) + '#'
        regex = 'TOTAL CPU TIME'
        line = re.search(regex, lines)
        if line is None:
            return False
        else:
            if line.group(0) != 'TOTAL CPU TIME':
                return False
            else:
                return True


def submit(jobs, nodes, crystal_path):
    job_numbers = len(jobs)
    max_paralell = 5
    count = 0
    submitted_jobs = []
    finished_jobs = []

    # find and submit the initial job
    loc = 0
    for job in jobs:
        if job.x == '0' and job.z == '0':
            break
        loc += 1
    if loc < len(jobs):
        job_init = jobs.pop(loc)
        os.chdir(job_init.path)
        if not if_cal_finish(job_init):
            copy_submit_scr(job_init, nodes, crystal_path)
            rename_file(job_init.path, 'geo_opt.out')
            out = submit_job(job_init, 'geo_opt')
            submitted_jobs.append(job_init)
            rec = job_init.path
            print(rec)
            rec += '\n'
            rec += 'job submitted...'
            rec += '\n' + out + '\n'
            rec += '---'*25
            record(job_init.root_path, rec)
            r = 0
            while True:
                if if_cal_finish(job_init):
                    rec = job_init.path
                    rec += '\n'
                    rec += 'calculation finished...'
                    record(job_init.root_path, rec)
                    submitted_jobs.remove(job_init)
                    finished_jobs.append(job_init)
                    break
                else:
                    time.sleep(500)
                    r += 1
                    # test function
                    test_init_job(job_init, r)
                    if r > 15:
                        rec = job_init.path
                        rec += '\n'
                        rec += 'initial calculation still not finished...'
                        record(job_init.root_path, rec)
                        r = 0
                    continue
        else:
            finished_jobs.append(job_init)

    # test if there is some job which is already finished
    for job in jobs[:]:
        if if_cal_finish(job):
            # print('Job already finished: ', job)
            finished_jobs.append(job)
            jobs.remove(job)

    def test_finished(paths):
        nonlocal count    # debug: UnboundLocalError: local variable 'count' referenced before assignment
        for path in paths[:]:
            if if_cal_finish(path):
                finished_jobs.append(path)
                num = str(len(finished_jobs)) + '/' + str(job_numbers)
                rec = path.path
                rec += '\n'
                rec += num + '   calculation finished.\n'
                rec += '---'*25
                print(rec)
                record(path.root_path, rec)
                paths.remove(path)
                count -= 1

    if len(jobs) == 0:
        return finished_jobs
    else:
        i = 0
        j = 0
        while True:
            test_finished(submitted_jobs)
            if len(finished_jobs) == job_numbers and len(submitted_jobs) == 0:
                break
            else:
                if count <= max_paralell and i < len(jobs):
                    print(jobs[i].path)
                    os.chdir(jobs[i].path)
                    copy_submit_scr(jobs[i], nodes, crystal_path)
                    copy_fort9(jobs[i])
                    rename_file(jobs[i].path, 'geo_opt.out')
                    rename_file(jobs[i].path, 'fort.9')
                    out = submit_job(jobs[i], 'geo_opt')
                    count += 1
                    submitted_jobs.append(jobs[i])
                    rec = jobs[i].path + '\n'
                    rec += 'job submitted.'
                    rec += '\n' + out + '\n'
                    rec += '---'*25
                    record(jobs[i].root_path, rec)
                    i += 1
                else:
                    time.sleep(500)
                    j += 1
                    j = test_calculation(j, submitted_jobs)     # test function
                    if j > 20:
                        rec = 'noting changes.\n'
                        rec += '---'*25
                        # print(rec)
                        record(submitted_jobs[0].root_path, rec)
                        j = 0
                    continue
    
        return finished_jobs


def test_calculation(j, submitted_jobs):
    # path = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\geo-opt'
    # walks = os.walk(path)
    # jobs = []
    # for root, dirs, files in walks:
    #     if 'hf.out' in files:
    #         job = Job(root)
    #         print(root)
    #         jobs.append(job)
    # print(jobs)
    if j == 1:
        out_file = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\geo-opt\x_a_2.5\d_int_3.10\hf.out'
        fort9_file = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\geo-opt\x_a_2.5\d_int_3.10\fort.9'
        for job in submitted_jobs:
            ziel_out = os.path.join(job.path, 'geo_opt.out')
            ziel_fort9 = os.path.join(job.path, 'fort.9')
            shutil.copy(out_file, ziel_out)
            shutil.copy(fort9_file, ziel_fort9)
        j = 0
        return j
    else:
        return j


def test_init_job(job_init, r):
    # ----------------------------------------- test ---------------------------------------------------
    if r == 1:
        out_file = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\geo-opt\x_a_2.5\d_int_3.10\hf.out'
        fort9_file = r'C:\Users\ccccc\Documents\Theoritische Chemie\Masterarbeit\BlackP\geo-opt\x_a_2.5\d_int_3.10\fort.9'
        ziel_out = os.path.join(job_init.path, 'geo_opt.out')
        ziel_fort9 = os.path.join(job_init.path, 'fort.9')
        shutil.copy(out_file, ziel_out)
        shutil.copy(fort9_file, ziel_fort9)
    # ----------------------------------------- test ---------------------------------------------------


def select_optimal_dist(job_geo_dict, diff, para):
    name, slab_or_molecule, group, lattice_parameter, bs_type, functional, nodes, crystal_path = para
    jobs = list(job_geo_dict.keys())
    init_job = jobs[0]
    init_dist = init_job.get_z_value()
    if diff == 0:
        New_Geo = GeoOPt.Select_Opt_Dis(job_geo_dict[init_job], init_job)
    elif diff >=1:
        New_Geo = GeoOPt.Select_Opt_Dis(job_geo_dict[init_job], init_job, direct=2)
    elif diff <= -1:
        New_Geo = GeoOPt.Select_Opt_Dis(job_geo_dict[init_job], init_job, direct=-2)
    new_geo = New_Geo.get_geo_series()
    new_geo_dict = {}
    for distance, geometry in new_geo.items():
        new_dist = distance
        new_z_dirname = 'z_{0:.3f}'.format(new_dist)
        old_z_dirmane = init_job.z_dirname
        new_path = init_job.path.replace(old_z_dirmane, new_z_dirname)
        new_job = Job(new_path)
        new_geo_dict[new_job] = geometry
        job_geo_dict[new_job] = geometry
    new_jobs = []
    jobs_finished = []
    for job, geometry in new_geo_dict.items():
        if not if_cal_finish(job):
            Geo_Inp = GeoOPt.Geo_Opt_Input(job, name, slab_or_molecule, group, lattice_parameter, geometry, bs_type, functional)
            Geo_Inp.gen_input()
            new_jobs.append(job)
        else:
            jobs_finished.append(job)
        jobs.append(job)
    new_jobs_finished = GeoOPt.submit(new_jobs, nodes, crystal_path)
    jobs_finished += new_jobs_finished
    min_dist, min_job = GeoOPt.read_and_select_lowest_e(jobs_finished)
    # print('MIN: ', min_dist, min_job)
    while True:
        jobs = sorted(jobs, key=lambda job: float(job.z))
        point = look_for_in_list(jobs, min_job)
        # print(jobs)
        # print(point)
        if (len(jobs) - point) == 1:
            New_Geo = GeoOPt.Select_Opt_Dis(job_geo_dict[min_job], min_job, direct=2)
        if (len(jobs) - point) == 2:
            New_Geo = GeoOPt.Select_Opt_Dis(job_geo_dict[min_job], min_job, direct=3)
        if (len(jobs) - point) >= 3:
            if len(jobs) >= 4 and point != 0:
                break
            else:
                New_Geo = GeoOPt.Select_Opt_Dis(job_geo_dict[min_job], min_job, direct=-2)
        new_geo = New_Geo.get_geo_series()
        new_geo_dict = {}
        for distance, geometry in new_geo.items():
            new_dist = distance + min_dist
            new_z_dirname = 'z_{0:.3f}'.format(new_dist)
            old_z_dirmane = min_job.z_dirname
            new_path = min_job.path.replace(old_z_dirmane, new_z_dirname)
            new_job = Job(new_path)
            new_geo_dict[new_job] = geometry
            job_geo_dict[new_job] = geometry
        new_jobs = []
        for job, geometry in new_geo_dict.items():
            if not if_cal_finish(job):
                print(job)
                Geo_Inp = GeoOPt.Geo_Opt_Input(job, name, slab_or_molecule, group, lattice_parameter, geometry, bs_type, functional)
                Geo_Inp.gen_input()
                new_jobs.append(job)
            else:
                jobs_finished.append(job)
            jobs.append(job)
        new_jobs_finished = GeoOPt.submit(new_jobs, nodes, crystal_path)
        jobs_finished += new_jobs_finished
        min_dist, min_job = GeoOPt.read_and_select_lowest_e(jobs_finished)
    return jobs, job_geo_dict, min_job, jobs_finished

# path = r'C:\Users\ccccc\PycharmProjects\Layer_Structure_Caculation\Test\geo_opt\x_0\z_0'
# update_nodes(path, nodes=14)


if __name__ == '__main__':
    test_calculation(1, [])
