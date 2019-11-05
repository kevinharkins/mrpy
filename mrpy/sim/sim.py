import numpy as np
import matplotlib.pyplot as pp

class Waveform:
    def __init__(self):
        self.t = []
        self.wave = []

    def append(self,t,wave):
        self.t.append(t)
        self.wave.append(wave)

    def sort(self):
        arg = np.argsort(self.t)
        self.t = self.t[arg]
        self.wave = self.wave[arg]
    
    def plot(self):
        pp.plot(self.t,self.wave)
        pp.show()

class SequenceSim:
    def __init__(self):
        self.grad = {}
    
    def run(self,seq):
        self.grad['R'] = Waveform()
        self.grad['P'] = Waveform()
        self.grad['S'] = Waveform()
        self.rf = Waveform()
        self.acq = Waveform()
        
        seq.run(self)
        
        f,(ax1,ax2) = pp.subplots(2,sharex=True)
        
        for t,wave in zip(self.rf.t,self.rf.wave):
            ax1.plot(t,wave,'b')
        for t,wave in zip(self.acq.t,self.acq.wave):
            ax1.plot(t,wave,'rx')
        for t,wave in zip(self.grad['R'].t,self.grad['R'].wave):
            hr = ax2.plot(t,wave,'b')
        for t,wave in zip(self.grad['P'].t,self.grad['P'].wave):
            hp = ax2.plot(t,wave,'r')
        for t,wave in zip(self.grad['S'].t,self.grad['S'].wave):
            hs = ax2.plot(t,wave,'g')
        
        ax1.set_ylabel('B1 (kHz)')
        ax1.legend(['RF pulse','ACQ'])
        ax1.grid(True)
        ax2.set_xlabel('time (ms)')
        ax2.set_ylim(-21,50)
        ax2.set_ylabel('gradient strength (mT/m)')
        ax2.legend([hr[0],hp[0],hs[0]],['Read','Phase','Slice'])
        ax2.grid(True)
        pp.show(block=True)

    
    def addGradient(self,gradobj):
        g,t,axis = gradobj.get_wave()
        self.grad[axis].append(t+gradobj.time,g)

    def addRF(self,rfobj):
        wave,phase,t = rfobj.get_wave()
        self.rf.append(t+rfobj.time,wave)
    
    def addAcquisition(self,acqobj):
        wave,t = acqobj.get_wave()
        self.acq.append(t+acqobj.time,wave)

    def addComposite(self,compobj):
        for part in compobj.parts:
            t0 = part.time
            part.time = part.time + compobj.time - part.anchor + compobj.anchor
            part.run(self)
            part.time = t0

    def addLoop(self,loopobj):
        t0 = loopobj.obj.time
        for n in np.arange(loopobj.nreps):
            loopobj.idx = n
            loopobj.obj.time =  n*loopobj.obj.dur + loopobj.time
            loopobj.obj.run(self)
        
        # reset list indexes & time
        loopobj.idx = None
        loopobj.obj.time = t0


