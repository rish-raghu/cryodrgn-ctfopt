#!/bin/bash

reference=$1
volumes=( $2 )
apix=$3

for volume in "${volumes[@]}"; do
    #sbatch -p cryoem -t 0:05:00 --mem=16G -J fsc --wrap "python ../../cryodrgn/analysis_scripts/fsc.py $reference $volume -o ${volume:0: -4}.fsc.txt --Apix $apix"
    echo $volume
    python ../../cryodrgn/analysis_scripts/fsc.py $reference $volume -o ${volume:0: -4}.fsc.txt --Apix $apix
done

#volumes=`ls results/open_fr1/100k/recon_ctf_post0.01/analyze*/kmeans5/vol_000_fsc.txt`
#sbatch -p cryoem --mem=16G -t 0:05:00 -J fsc --wrap "python cryodrgn/analysis_scripts/plotfsc.py $volumes --labels 14 19 24 29 34 39 44 4 9 -o fsc.png --title 'FSC Across Training Epochs'"
