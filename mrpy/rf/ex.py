import numpy as np
from mrpy.limits import *
from mrpy.seq import RFChain

class RFPulse(RFChain):
    req_parms= ('dur','flip',)
    anchor = None
    time = 0
    ph_cycle = (0,)
    dfdz = None
    
    def get_wave(self):
        return self.wave,self.phase,self.t
    
    def run(self,machine):
        return machine.addRF(self)

class Block(RFPulse):
    tbw = 2 # later: what is this really?
        
    def build(self):
        if self.anchor is None:
            self.anchor = self.dur/2
        
        self.bw = self.tbw/self.dur
        self.b1 = self.flip/360./self.dur # kHz
        self.t = np.array([0, 0, self.dur, self.dur])# - self.anchor
        self.wave = np.array([0, self.b1, self.b1, 0])
        self.phase = np.zeros(wave.shape)

class Gauss(RFPulse):
    tbw = 2.74 # later: what is this really?
    res=GradientLimits.dwell
        
    def build(self):
        if self.anchor is None:
            self.anchor = self.dur/2
        
        self.bw = self.tbw/self.dur
        
        self.t = np.arange(0,self.dur,self.res)# - self.anchor
        wave = np.exp(-(self.t-self.anchor)**2*9/(self.dur**2))
        self.b1 = wave/np.sum(wave)/self.res*self.flip/360.
        self.wave = wave*self.b1
        self.phase = np.zeros(wave.shape)

