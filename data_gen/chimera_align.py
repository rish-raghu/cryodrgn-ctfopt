from chimerax.core.commands import run

APIX = 1.05
REF_MAP_DIM = 400
REF_MAP = 'data/covidSpike/maps/exp_closed/emd_closed.map'
STRUCTURE = 'data/covidSpike/mdsims/{}-no-water-zinc-glueCA/trajectories/DESRES-Trajectory_S.mae'
OUTFILE = 'data/covidSpike/mdsims/{}-no-water-zinc-glueCA/trajectories/align.positions'

def remove_glycans(model_id):
    remove_list = ['F2A', 'NM5', 'NLM', 'NM7', 'H2A', 'ACE', 'NME']
    for name in remove_list:
        run(session, 'delete #{}::name=\"{}\"'.format(model_id, name))


center = REF_MAP_DIM/2 * APIX

run(session, 'open {}'.format(REF_MAP))
run(session, 'open {}'.format(STRUCTURE.format('closed')))
run(session, 'open {}'.format(STRUCTURE.format('open')))
run(session, 'combine #2 close true')
run(session, 'combine #3 close true')
run(session, 'move {0},{0},{0} coordinateSystem #1 models #2,3'.format(center))
remove_glycans(2)
remove_glycans(3)
run(session, 'fitmap #2 in #1')
run(session, 'rmsd #3 to #2')
run(session, 'align #3 to #2')
run(session, 'save {} models #2'.format(OUTFILE.format('closed')))
run(session, 'save {} models #3'.format(OUTFILE.format('open')))
run(session, 'exit')
