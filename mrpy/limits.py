import numpy as np

gamma = 42.57747892 * 2 * np.pi # kHz/mT

class GradientLimits:
    grad_max = 750 # mT/m
    grad_lim = 400.0 # mT/m
    rise_time = 0.200 # ms
    dwell = 0.004 # ms
