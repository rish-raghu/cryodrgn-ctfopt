#!/bin/bash

ref=$1
dir=$2
skip=$3

numVols=( $dir/reconstruct.*.mrc ) 
numVols=${#numVols[@]}
echo $numVols volumes total
echo Skip: $skip

for ((i=2; i<$numVols; i+=skip)); do
    vol=$dir/reconstruct.$i.mrc
    echo $vol
    /scratch/gpfs/rraghu/chimerax-1.5/bin/ChimeraX --nogui --script "../../ez_tools/chimerax_align.py $ref $vol -o ${vol:0: -4}.align.mrc -f ${vol:0: -4}.align.txt --flip" > ${vol:0: -4}.align.txt
done
