#!/bin/bash
#PBS -j eo
#PBS -r n
#PBS -l nodes=1
#ulimit -S -s 131072

cd ${PBS_O_WORKDIR}
path0=${PWD%/*}
dirname1=${path0##/*/}
path1=${path0%/*}
dirname2=${path1##/*/}
dirname0=${PWD##/*/}
dir0=/scratch/shch/cryscor/$dirname2/$dirname1/$dirname0
mkdir -p $dir0
cp inp_Slab1 $dir0
cp fort.9 $dir0
cp fort.78 $dir0
cp fort.80 $dir0
cp ~/project/cryscor $dir0
cd $dir0

module load XE2016.0.3.210

export MKL_NUM_THREADS=1
#module load /srv/opt/Modules/IntelCompiler/XE2016.0.3.210

./cryscor < inp_Slab1 > lmp2.out 2>lmp2.err


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

