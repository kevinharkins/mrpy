import numpy as np
from mrpy.ss import SliceSelection
from mrpy.seq import Sequence, Composite, Loop, List
from mrpy.encoding import CartesianEncoding

class Contrast(Sequence):
    pass

class GradientEcho(Composite):
    '''
        GradientEcho(Composite) is a gradient echo imaging pulse sequence
    '''
    req_parms = ('te','tr','nr','na','ss','enc')
    nr = 1 # default number of repetitions
    na = 1 # default number of averages
    
    # any Composite objects that are saved as req_parms need to be reloaded as objects
    def load(self):
        self.ss = SliceSelection(**self.ss)
        self.enc = CartesianEncoding(**self.enc)
    
    def build_base(self):
        # define slice select rf and gradient pulses
        self.ss.thk = self.enc.fov[2]
        self.ss.after.anchor = 0
        
        # pre build the ss and enc objects to calculate other minimum durations
        self.ss.build()
        self.enc.build()
        
        # Calculate the minimum echo time, and update the sequence
        min_te = ( self.ss.dur-self.ss.anchor + 
            max(self.ss.after.dur,self.enc.before.dur) +  # these will be combined
            self.enc.readout.anchor )
        self.te = max(min_te,self.te)
        
        # allow duration of the pre-encoding gradients to be expanded to the limit of the 
        # RO duration
        pre_enc_dur = self.enc.before.dur + self.te-min_te
        pre_enc_dur = min(pre_enc_dur,self.enc.readout.dur) 
        
        # calculate min TR
        min_tr = (self.enc.readout.dur - self.enc.readout.anchor + 
            self.te + 
            self.enc.after.dur + 
            self.ss.anchor)
        self.tr = max(min_tr,self.tr)
        
        # allow duration of the post-encoding gradients to be expanded to the limit of the
        # RO duration
        post_enc_dur = self.enc.after.dur + self.tr - min_tr
        post_enc_dur = min(post_enc_dur,self.enc.readout.dur) 
        
        # rebuild ss and enc objects with final durations
        self.ss.build(after_dur=pre_enc_dur)
        self.enc.build(before_dur=pre_enc_dur,after_dur=post_enc_dur)
        
        # add ss refocusing pulse to before_readout
        self.enc.before.add(self.ss.after)
        
        self.enc.readout.time = self.te
        self.enc.before.anchor = 0
        self.enc.before.time = self.ss.dur - self.ss.anchor
        self.enc.after.anchor = 0
        self.enc.after.time = self.te + self.enc.readout.dur-self.enc.readout.anchor
        
        # the base sequence contains slice selection, readout, encoding (todo: spoiling)
        self.base = Composite(dur=self.tr,
            parts=(self.ss,self.enc.readout,self.enc.before,self.enc.after))
        self.base.anchor = self.ss.anchor
        
    def build(self):
        self.build_base()
        
        # add averaging Loop
        la = Loop(obj=self.base)
        la.name = 'avg'
        la.add_list(List(np.arange(self.na)))
        la.build()
        
        # add PE1 loop
        l1 = Loop(obj=la)
        l1.name = 'pe1'
        l1.add_list(self.enc.pe1_grad.gmax)
        l1.add_list(self.enc.pe1r_grad.gmax)
        l1.build()
        
        # add PE2 loop
        l2 = Loop(obj=l1)
        l2.name = 'pe2'
        l2.add_list(self.enc.pe2_grad.gmax)
        l2.add_list(self.enc.pe2r_grad.gmax)
        l2.build()
        
        # add rep loop
        lr = Loop(obj=l2)
        lr.name = 'nrep'
        lr.add_list(List(np.arange(self.nr)))
        lr.build()
        
        self.add(lr)
        
