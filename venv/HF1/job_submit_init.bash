#!/bin/bash
#PBS -j eo
#PBS -r n
#PBS -l nodes=12


module load XE2016.0.3.210
export MPIROOT=/opt/intel/XE2016.U3/compilers_and_libraries_2016.3.210/linux/mpi/intel64
export PATH=${MPIROOT}/bin:${PATH}

cd ${PBS_O_WORKDIR}
currdir=/scratch/$USER/$$tmp
crystal_path=~usvyat/Crystal14_new/bin/Linux-ifort-i64-t/std
mkdir -p $currdir
cp INPUT $currdir
cd $currdir

mpirun -np 12 $crystal_path/Pcrystal >& ${PBS_O_WORKDIR}/hf.out

cp fort.9 ${PBS_O_WORKDIR}/
cd ${PBS_O_WORKDIR}
rm -r $currdir

