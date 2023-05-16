import numpy as np
from cryodrgn.beta_schedule import LinearSchedule

def get_barf_schedule(end_iter, num_freqs):
    return LinearSchedule(0, num_freqs, 0, end_iter)
