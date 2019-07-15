#!/bin/bash
#PBS -j eo
#PBS -r n
#PBS -l nodes=28

module load XE2016.0.3.210
export MOLPRO_KEY='id=teomgs,date=:2018/12/07,version=:9999,mpp=32767,password=EyuC2ci4yQIRsSKd&XlH8psYIc8FbHn3F'
export PATH=.:~/Molpro/bin:~/Molpro/lib/:${PATH}

cd ${PBS_O_WORKDIR}
path0=${PWD%/*}
zdirname=${path0##/*/}
path1=${path0%/*}
xdirname=${path1##/*/}
layertype=${PWD##/*/}

export scr1=/scratch/$LOGNAME
export SCRATCHDIR=/scratch/$USER/lmp2/$xdirname/$zdirname/$layertype
export TMPDIR=$SCRATCHDIR
export TMPDIR4=$scr1/run
export TMPDIR5=$scr1/run
export TMPDIR6=$scr1/run


/users/$USER//Molpro/bin/molpro -n 23 rpa.inp -d ${SCRATCHDIR} -I ${SCRATCHDIR} -W ${SCRATCHDIR}
rm ${SCRATCHDIR}/*TMP