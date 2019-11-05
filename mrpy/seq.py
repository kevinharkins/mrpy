import numpy as np
from mrpy.limits import *

class System: pass

class Sequence:
    req_parms = None
    name = None
    
    def __init__(self, **kwargs):
        for parm in kwargs:
            setattr(self,parm,kwargs[parm])
        
        self.load()
        self.build()
        
    def load(self):
        pass
    
    def min_time(self):
        return self.anchor - self.time
    
    def max_time(self):
        return (self.dur-self.anchor) - self.time    
    
    def serialize(self):
        raise Exception('Only Composite objects can be serialized')

class RFChain(Sequence):
    pass

class Acquisition(RFChain):
    req_parms = ('npoints','dwell')
    time = 0
    anchor = None
    ph_cycle = (0,)
    dfdz = None
    
    def build(self):
        self.dur = self.npoints*self.dwell
        
        if self.anchor is None:
            self.anchor = self.dur/2
    
    def get_wave(self):
        t = np.arange(0,self.npoints)*self.dwell#- self.anchor
        g = np.zeros(t.shape)
        return g,t
    
    def run(self,machine):
        return machine.addAcquisition(self)


class Composite(Sequence):
    '''
    Composite(Sequence) is a general container for other pulse sequence objects
    
        Composite(dur,parts,anchor,time)
        dur = duration of the composite object
        parts = other sequence objects that will be children to this object
        anchor = reference point in time relative to the beginning of the object, ms
        time = placement the anchor inside the parent sequence element, ms
    '''
    dur = 0
    parts = None
    anchor = 0
    time = 0
    
    def add(self,obj):
        if self.parts is None:
            self.parts = []
        self.parts.append(obj)
        
    def build(self):
        if self.parts is None:
            self.parts = []
            
        for part in self.parts:
            part.build()
    
    def serialize(self):
        if self.req_parms is None:
            raise Exception('Composite must be extended before it can be serialized')
            
        d = dict();
        for parm in self.req_parms:
            #print(parm,getattr(self,parm),isinstance(getattr(self,parm), Composite))
            if isinstance(getattr(self,parm), Composite):
                d[parm] = getattr(self,parm).serialize()
            else:
                d[parm] = getattr(self,parm)
        return d
    
    def run(self,machine):
        return machine.addComposite(self)

class Loop(Sequence):
    '''
    Loop(Sequence) provides logic to loop through a composite object while iterating over 
    lists inside the object
    
        Loop(obj,lists)
        obj = the sequence object to be repeated
        lists = vector of List objects that this 
    '''
    obj = None # the object being iterated over
    lists = None # list of Lists this loop increments
    time = 0 # relative to the outer composite sequence
    idx = None # current 
    anchor = 0
    
    def add_list(self,list):
        list.loop = self
        if self.lists is None:
            self.lists = []
        self.lists.append(list)
        
    def build(self):
        if self.lists is not None:
            self.nreps = len(self.lists[0])
            for list in self.lists:
                if len(list) != self.nreps:
                    raise "All lists in a loop must have the same number of values"
        
            self.dur = self.obj.dur*self.nreps
            try:
                self.objdur = self.obj.objdur
            except:
                self.objdur = self.obj.dur
    
    def run(self,machine):
        return machine.addLoop(self)

class List:
    def __init__(self,vals,loop=None):
        if np.isscalar(vals):
            vals = [vals,]
        self.vals = np.array(vals)
        self.loop = loop
    
    def value(self):
        if self.loop is None or self.loop.idx is None:
            imax = np.argmax(np.abs(self.vals))
            val = self.vals[imax]
        else:
            val = self.vals[self.loop.idx]
            
        return val
        
    def __len__(self):
        return len(self.vals)
    
    def __repr__(self):
        return 'List: ' + repr(self.vals)
        
    """ Basic +-*/ """
    def __add__(self, other):
        if isinstance(other, List):
            other = other.vals
        
        return List(self.vals + other)
    
    def __mul__(self, other):
        if isinstance(other, List):
            other = other.vals
        
        return List(self.vals * other)
        
    def __rmul__(self,other):
        if isinstance(other, List):
            other = other.vals
        
        return List(self.vals * other)
    
    def __sub__(self, other):
        if isinstance(other, List):
            other = other.vals
        
        return List(self.vals - other)
    
    def __truediv__(self, other):
        if isinstance(other, List):
            other = other.vals
        
        return List(self.vals / other)

