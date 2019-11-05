import numpy as np
from . import Encoding
import mrpy.seq as seq
import mrpy.limits as limits
from mrpy.grad import trap

class CartesianEncoding(seq.Composite):
    req_parms = ('fov','img_matrix','dwell','enc_matrix')
    offset = np.array([0,0,0])
    dwell = 0.020
    enc_matrix = None
    
    def build(self,before_dur=0,after_dur=0):
    
        if self.enc_matrix is None:
            self.enc_matrix = self.img_matrix
        
        self.resol = self.fov/self.img_matrix
        
        ##########################
        # build readout gradient and acquisition
        ##########################
        grad_str = 2*np.pi/self.dwell/self.fov[0]/limits.gamma * 1000 # mT/m
        dur = self.enc_matrix[0]*self.dwell
        self.ro_grad = trap.ConstGradient(gmax=grad_str,top_dur=dur,axis='R')
        self.ro_grad.anchor = self.ro_grad.dur/2
        self.acq = seq.Acquisition(dwell=self.dwell,npoints=self.enc_matrix[0])
        self.acq.dfdz = limits.gamma/2/np.pi*grad_str
        
        ##########################
        # build pre-encoding gradients
        ##########################
        pp_area = -self.ro_grad.area/2
        pe1_area = -np.pi*(self.enc_matrix[1]-1)/self.fov[1]/limits.gamma * 1000 # mT/m
        npe1 = self.enc_matrix[1]/2
        pe1_list = seq.List(np.arange(np.floor(-npe1+1),np.floor(npe1)+1)/npe1)
        pe2_area = -np.pi*(self.enc_matrix[2]-1)/self.fov[2]/limits.gamma * 1000 # mT/m
        npe2 = self.enc_matrix[2]/2
        pe2_list = seq.List(np.arange(np.floor(-npe2+1),np.floor(npe2)+1)/npe2)
        
        min_dur = trap.TrapGradient.calc_min_dur(pp_area)
        min_dur = max(min_dur,trap.TrapGradient.calc_min_dur(pe1_area))
        min_dur = max(min_dur,trap.TrapGradient.calc_min_dur(pe1_area))
        
        before_dur = max(before_dur,min_dur)
        self.pp_grad = trap.TrapGradient.by_area(area=pp_area,dur=before_dur,axis='R')
        self.pe1_grad = trap.TrapGradient.by_area(area=pe1_area*pe1_list,dur=before_dur,axis='P')
        self.pe2_grad = trap.TrapGradient.by_area(area=pe2_area*pe2_list,dur=before_dur,axis='S')
        
        ##########################
        # create copies for post readout
        ##########################
        after_dur = max(after_dur,min_dur)
        self.ppr_grad = trap.TrapGradient.by_area(area=pp_area,dur=after_dur,axis='R')
        self.pe1r_grad = trap.TrapGradient.by_area(area=-pe1_area*pe1_list,dur=after_dur,axis='P')
        self.pe2r_grad = trap.TrapGradient.by_area(area=-pe2_area*pe2_list,dur=after_dur,axis='S')
        
        ##########################
        # create the composite objects interfaced by other sequences
        ##########################
        self.readout = seq.Composite(dur=self.ro_grad.dur,parts=[self.ro_grad,self.acq])
        self.readout.anchor = self.readout.dur/2
        self.before = seq.Composite(dur=before_dur,parts=[self.pp_grad,self.pe1_grad,self.pe2_grad])
        self.after = seq.Composite(dur=after_dur,parts=[self.ppr_grad,self.pe1r_grad,self.pe2r_grad])

