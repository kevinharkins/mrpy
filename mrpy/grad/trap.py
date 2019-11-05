import numpy as np
from mrpy.limits import *
from mrpy.seq import Sequence, List

class Gradient(Sequence):
    def run(self,machine):
        return machine.addGradient(self)

class TrapGradient(Gradient):
    '''
    TrapGradient defines a trapezoidal gradient waveform.
    
        TrapGradient(gmax,dur,axis)
        gmax = max amplitude of the gradient, mT/m
        dur = total duration of the gradient waveform, ms
        axis = 'R' (read), 'P' (phase), or 'S' (slice)
        
        Other parameters:
        anchor = reference point in time relative to the beginning of the waveform, ms
        time = placement the anchor inside the parent sequence element, ms
        trise = rise time of the gradient waveform, ms 
        tfall = fall time of the gradient waveform, ms
        
        Calculated parameters:
        area = area of the gradient waveform, ms*mT/m
    '''
    trise=GradientLimits.rise_time
    tfall=GradientLimits.rise_time
    anchor = 0
    time = 0
    
    def load(self):
        if not isinstance(self.gmax,List):
            self.gmax = List(self.gmax)
        
    def build(self,area=None,dur=None):
        self.area = (2*self.dur-self.trise-self.tfall)/2*self.gmax.value() # ms*mT/m
        
    def get_wave(self):
        self.t = np.array([0, self.trise, self.dur-self.tfall, self.dur])# - self.anchor
        self.g = np.array([0, self.gmax.value(), self.gmax.value(), 0])
        return self.g,self.t,self.axis
    
    @staticmethod
    def by_area(area,dur=0,axis='S',anchor=0,time=0):
        min_dur = TrapGradient.calc_min_dur(area)
        dur = max(dur,min_dur)
        gmax = 2.0*area/(2.0*dur-TrapGradient.trise-TrapGradient.tfall)
        
        return TrapGradient(gmax=gmax,dur=dur,axis=axis,anchor=anchor,time=time)
    
    @staticmethod
    def calc_min_dur(area):
        try:
            area = area.value()
        except:
            pass # this is not a List, carry on
        
        min_dur = (np.abs(area)*2.0/GradientLimits.grad_lim + TrapGradient.trise + TrapGradient.tfall)/2.0
        min_dur = max(min_dur,TrapGradient.trise + TrapGradient.tfall)
        return min_dur

class ConstGradient(TrapGradient):
    '''
    ConstGradient(TrapGradient) defines a trapezoidal gradient waveform that requires a 
    specific gradient strength, like that used for conventional slice selection and 
    readout
    
        ConstGradient(gmax,top_dur,axis)
        gmax = max amplitude of the gradient, mT/m
        top_dur = duration of the gradient waveform at gmax, ms
        axis = 'R', 'P', or 'S'
        
        Other parameters:
        anchor = reference point in time relative to the beginning of the waveform, ms
        time = placement the anchor inside the parent sequence element, ms
        trise = rise time of the gradient waveform, ms 
        tfall = fall time of the gradient waveform, ms
        
        Calculated parameters:
        dur = top_dur + trise + tfall, ms
        area = area of the gradient waveform, ms*mT/m
    '''
        
    def build(self):
        self.dur = self.top_dur + self.trise + self.tfall # ms
        
        if self.anchor == None:
            self.anchor = self.dur/2
            
        self.area = (2*self.dur-self.trise-self.tfall)/2*self.gmax.value() # ms*mT/m
