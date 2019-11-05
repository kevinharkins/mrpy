from . import ex
from . import rfc

excitation_pulses = {
    'bloch': ex.Block, 
    'gauss': ex.Gauss,
}

refocusing_pulses = {
    'bloch': rfc.Block,
    'gauss': rfc.Gauss,
}