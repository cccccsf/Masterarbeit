#!/usr/bin/python3
import os


class Scr(object):

    def __init__(self, job, nodes, molpro_key, molpro_path):
        self.job = job
        self.path = job.path
        self.scr_path = os.path.join(self.path, 'rpa')
        self.nodes = nodes
        self.molpro_key = molpro_key
        self.molpro_path = molpro_path

    def gen_scr(self):

        if self.job.layertype == 'bilayer':
            scratchDir = '/scratch/$USER/lmp2/{}/{}'.format(self.job.x_dirname, self.job.z_dirname)
        else:
            scratchDir = '/scratch/$USER/lmp2/{}/{}/{}'.format(self.job.x_dirname, self.job.z_dirname, self.job.layertype)

        with open(self.scr_path, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('#PBS -j eo\n')
            f.write('#PBS -r n')
            f.write('#PBS -l nodes={}\n'.format(self.nodes))
            f.write('\n')

            f.write('module load XE2016.0.3.210\n')
            f.write('export MOLPRO_KEY={}\n'.format(self.molpro_key))
            f.write('export PATH=.:{}/bin:{}/lib/:${{PATH}}\n'.format(self.molpro_path, self.molpro_path))
            f.write('\n')

            f.write('cd ${PBS_O_WORKDIR}\n')
            f.write('export scr1=/scratch/$LOGNAME\n')
            f.write('export SCRATCHDIR={}\n'.format(scratchDir))
            f.write('export TMPDIR=$SCRATCHDIR\n')
            f.write('export TMPDIR4=$scr1/run\n')
            f.write('export TMPDIR5=$scr1/run\n')
            f.write('export TMPDIR6=$scr1/run\n')
            f.write('\n')

            f.write('molpro -n {} rpa.inp -d ${{SCRATCHDIR}} -I ${{SCRATCHDIR}} -W ${{SCRATCHDIR}}\n'.format(self.nodes))
            f.write('rm ${SCRATCHDIR}/*TMP\n')
