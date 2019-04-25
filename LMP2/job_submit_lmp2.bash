#!/bin/bash
#PBS -j eo
#PBS -r n
#PBS -l nodes=1


module load XE2016.0.3.210
export MKL_NUM_THREADS=1

cd ${PBS_O_WORKDIR}
cryscor_path=~shch/project/
currdir=/scratch/$USER/lmp2/x_0/z_0
mkdir -p $currdir
cp INPUT $currdir
cp fort.9 $currdir
cp fort.78 $currdir
cp fort.80 $currdir
cp $cryscor_path/cryscor $currdir
cd $currdir

./cryscor < INPUT > lmp2.out 2>lmp2.err


cp lmp2.out ${PBS_O_WORKDIR}
mv fort.177 _fort.177
mv fort.178 _fort.178
mv fort.179 _fort.179
mv fort.180 _fort.180
mv fort.181 _fort.181

rm fort*

mv _fort.177 fort.177
mv _fort.178 fort.178
mv _fort.179 fort.179
mv _fort.180 fort.180
mv _fort.181 fort.181

rm INT2IDX_DF*
cp molpro.inp ${PBS_O_WORKDIR}
