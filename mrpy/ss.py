import numpy as np
from mrpy.rf import excitation_pulses
import mrpy.grad as grad
import mrpy.limits as limits
from mrpy.seq import Composite

class SliceSelection(Composite):
    req_parms= ('thk','flip','pulse_dur','pulse')
    pulse = 'gauss'
    anchor = None
    time = 0
        
    def build(self,after_dur=0):
        pulse_inst = excitation_pulses[self.pulse](dur=self.pulse_dur,flip=self.flip)
        g = 2 * np.pi * pulse_inst.bw/limits.gamma/self.thk * 1000 # mT/m
        self.gs = grad.ConstGradient(gmax=g,top_dur=self.pulse_dur,axis='S')
        self.gs.anchor = self.gs.dur/2
        
        pulse_inst.dfdz = limits.gamma/2/np.pi*g
        
        if self.anchor is None:
            self.anchor = self.gs.anchor
        
        self.parts = (pulse_inst,self.gs)
        ssr = grad.TrapGradient.by_area(area=-self.gs.area/2.0,dur=after_dur,axis='S')
        self.after = Composite(dur=0,parts=(ssr,))
        self.after.time = self.time
        self.before = ()
        self.dur = self.gs.dur

