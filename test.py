import numpy as np
from mrpy.gradientecho import GradientEcho
from mrpy.sim import SequenceSim
#from mrpy.bruker import Paravision601

parms = {
    'tr': 200.0, # repetition time (ms)
    'te': 4.0, # echo time (ms)
    'ss': { # options for slice selection module
        'thk': 5, # slice thickness (mm)
        'flip': 20, # flip angle (degrees)
        'pulse_dur': 2.0, # pulse duration (ms)
        'pulse': 'gauss' # pulse type 
    },
    'enc': { # options for encoding module
        'fov': np.array([30., 30., 2.0]), # field of view (mm)
        'img_matrix': np.array([64,64,1]), # matrix size
        'dwell': 0.020 # receiver dwell time (ms)
    },
}

ge = GradientEcho(**parms)

# run sequence in the simulator
s = SequenceSim()
s.run(ge)

# translate to Paravision 6, commented out for now
#pv = Paravision601()
#pv.run(ge)

