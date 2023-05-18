from chimerax.core.commands import run
import subprocess, shlex
import argparse
import os

APIX = 1.05
REF_MAP_DIM = 400
TOTAL_NUM_FRAMES = 8334
FRAMES_PER_TRAJ = 1000

REF_MAP = '/scratch/gpfs/rraghu/data/covidSpike/maps/exp_closed/emd_closed.map'
STRUCTURE = '/scratch/gpfs/rraghu/data/covidSpike/mdsims/{}-no-water-zinc-glueCA/trajectories/DESRES-Trajectory_S.mae'
TRAJ = '/scratch/gpfs/rraghu/data/covidSpike/mdsims/{}-no-water-zinc-glueCA/trajectories/S-000{}.dcd'
ALIGN_MATRIX = '/scratch/gpfs/rraghu/data/covidSpike/mdsims/{}-no-water-zinc-glueCA/trajectories/align.positions'

parser = argparse.ArgumentParser()
parser.add_argument('state', type=str, help='open or closed')
parser.add_argument('-o', required=True, help='Output directory')
parser.add_argument('--start_frame', type=int, default=1, help='First frame to generate, 1-indexed')
parser.add_argument('--end_frame', type=int, default=TOTAL_NUM_FRAMES, help='Last frame to generate, 1-indexed')
parser.add_argument('--target_dim', type=int, default=256, help='Dimension of output grids')
args = parser.parse_args()

center = REF_MAP_DIM/2 * APIX
new_apix = round(APIX * REF_MAP_DIM / args.target_dim, 2)
resolution = new_apix * 2 # Nyquist freq
print("New Apix = ", new_apix)

# Open closed volume and desired structure
run(session, 'open {}'.format(REF_MAP))
run(session, 'open {}'.format(STRUCTURE.format(args.state)))
run(session, 'combine #2 close true')

# Mark all atoms whose density should not be computed (e.g. glycans)
exclude_list = ['F2A', 'NM5', 'NLM', 'NM7', 'H2A', 'ACE', 'NME']
for name in exclude_list:
    run(session, 'setattr #2::name=\"{}\" residues name EXC'.format(name))

# Apply alignment transformations
run(session, 'move {0},{0},{0} coordinateSystem #1 models #2'.format(center))
run(session, 'open {} models #2'.format(ALIGN_MATRIX.format(args.state)))

# Generate volumes on grid of reference map
run(session, 'volume new empty size {} gridSpacing {}'.format(REF_MAP_DIM, APIX))
curr_traj = -1
for frame in range(args.start_frame-1, args.end_frame):
    if frame//FRAMES_PER_TRAJ != curr_traj:
        curr_traj = frame//FRAMES_PER_TRAJ
        run(session, 'open {} structureModel #2'.format(TRAJ.format(args.state, curr_traj)))
    run(session, 'coordset #2 {}'.format(frame%FRAMES_PER_TRAJ + 1))
    run(session, 'molmap #2::name!=EXC {} gridSpacing {}'.format(resolution, APIX))
    run(session, 'volume add #4 #3 onGrid #3')
    run(session, 'save {} models #5'.format(os.path.join(args.o, 'molmap{:04d}.mrc'.format(frame+1))))
    run(session, 'close #4,5')

    # Downsample volume
    # NOTE: downsampled volume has Apix=1 in header, not new_apix; 
    # change in chimera with 'volume model# voxelSize new_apix'
    downsample_cmd = "cryodrgn downsample {} -D {} --is-vol -o {}".format(
        os.path.join(args.o, 'molmap{:04d}.mrc'.format(frame+1)),
        args.target_dim,
        os.path.join(args.o, 'molmap{:04d}.mrc'.format(frame+1))
    )
    subprocess.run(shlex.split(downsample_cmd))

run(session, 'exit')
