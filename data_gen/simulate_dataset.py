import subprocess, shlex
import argparse
import os
import glob
import math

parser = argparse.ArgumentParser()
parser.add_argument('state', type=str, help='open or closed')
parser.add_argument('num_frames', type=int, help='Number of frames to generate volumes from')
parser.add_argument('imgs_per_frame', type=int, help='Number of images to generate in per frame')
parser.add_argument('-o', required=True, help='Output directory')
parser.add_argument('--target_dim', type=int, default=256, help='Dimension of output grids')
parser.add_argument('--batch_size', type=int, default=1000, help='Number of frames to generate before projecting')
parser.add_argument('--imgs_per_outfile', type=int, default=50000, help='Number of images in each output mrc file')
parser.add_argument('--seed', type=int, default=None, help='Seed for random rotations/translations')
args = parser.parse_args()

if args.imgs_per_outfile % args.imgs_per_frame != 0:
    raise IllegalArgumentException("imgs_per_outfile must be divisible by imgs_per_frame")
frames_per_outfile = min(args.imgs_per_outfile // args.imgs_per_frame, args.num_frames)

molmap_cmd = "/scratch/gpfs/rraghu/chimerax-1.5/bin/ChimeraX --nogui --script \"/scratch/gpfs/rraghu/scripts/chimera_molmap.py {} -o {} --start_frame {} --end_frame {}\""
project_cmd = "python /scratch/gpfs/rraghu/cryosim/multiproject3d.py {} -n {} -o {} --out-pose {} --t-extent 10 -b 20"
if args.seed: project_cmd += " --seed {}".format(args.seed)

mrcs_num = 0
for batch_num in range(math.ceil(args.num_frames/args.batch_size)):
    cmd = molmap_cmd.format(args.state, args.o, batch_num*args.batch_size+1, min((batch_num+1)*args.batch_size, args.num_frames))
    subprocess.run(shlex.split(cmd))
    vol_files = sorted(glob.glob(os.path.join(args.o, 'molmap*.mrc')))

    for out_num in range(math.ceil(min(args.batch_size, args.num_frames)/frames_per_outfile)):
        cmd = project_cmd.format(
            " ".join(vol_files[out_num*frames_per_outfile: min((out_num+1)*frames_per_outfile, len(vol_files))]), 
            args.imgs_per_frame, 
            os.path.join(args.o, 'proj{:02d}.mrcs'.format(mrcs_num)),
            os.path.join(args.o, 'poses{:02d}.pkl'.format(mrcs_num)))
        subprocess.run(shlex.split(cmd))
        mrcs_num += 1
    
    for file in vol_files:
        os.remove(file)
