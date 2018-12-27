#!/bin/bash
#PBS -j eo
#PBS -r n
#PBS -l nodes=14



cd ${PBS_O_WORKDIR}
currdir=/scratch/$USER/$$tmp
mkdir -p $currdir
cp INPUT $currdir
cd $currdir
/srv/opt/intel/XE2016.U3/compilers_and_libraries_2016.3.210/linux/mpi/intel64/bin/mpirun -np 14 ~usvyat/Crystal14_new/bin/Linux-ifort-i64-t/std/Pcrystal >& ${PBS_O_WORKDIR}/hf.out

cp fort.9 ${PBS_O_WORKDIR}/
cd ${PBS_O_WORKDIR}
rm -r $currdir

