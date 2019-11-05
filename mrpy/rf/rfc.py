import numpy as np
from mrpy.limits import *
from .ex import RFPulse

class Block(RFPulse):
    tbw = 2 # later: what is this really?

    def __init__(self,dur,flip,anchor=None,time=0):
        self.dur = dur
        self.flip = flip
        self.b1 = flip/360./dur # kHz
        
        if anchor == None:
            anchor = dur/2
        
        self.anchor = anchor
        self.time = time
        
        self.build()
        
    def build(self):
        self.bw = self.tbw/self.dur

    def get_wave(self):
        t = np.array([0, 0, self.dur, self.dur]) - self.anchor
        wave = np.array([0, self.b1, self.b1, 0])
        phase = np.zeros(wave.shape)
        return wave,phase,t

class Gauss(RFPulse):
    tbw = 2 # later: what is this really?
    
    def __init__(self,dur,flip,anchor=None,time=0,res=GradientLimits.dwell):
        self.dur = dur
        self.flip = flip # degrees
        self.b1 = None # kHz
        if anchor == None:
            anchor = dur/2
            
        self.anchor = anchor
        self.time = time
        self.res = res
        
        self.build()
        
    def build(self):
        self.bw = self.tbw/self.dur

    def get_wave(self):
        t = np.arange(0,self.dur,self.res) - self.anchor
        wave = np.exp(-(t)**2*9/(self.dur**2))
        self.b1 = wave/np.sum(wave)/self.res*self.flip/360.
        wave = wave*self.b1
        phase = np.zeros(wave.shape)
        return wave,phase,t
