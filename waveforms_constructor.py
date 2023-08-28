import numpy as np
import matplotlib.pyplot as plt

class qubit:
    
    #this class defines a qubit object
    
    def __init__(self,freq,probe_freq):
        # class constructor
        self.freq       = freq # in Hz   #frequency of the qubit
        self.LO_freq    = freq # in Hz   #fequency  of the local oscillator for IQ mixer control line
        self.IF_freq    = 0 #!    # in Hz   #IF - intermideate waveform modulation frequency IF=LO_freq-freq
        
        self.probe_freq = probe_freq # in Hz # frequency of the probe resonator for the qubit
        
        self.pi_amp     = 0              # amplitide of the gaussian pi-pulse
        self.half_pi_amp = 0
        self.pi_dur     = 25E-9 # in sec # time constant of the gaussian pi-pulse
        
        self.I          = 0.5            # 
        self.Q          = 0.5*1j
             
        
    def set_freq(self,freq):
        # sets qubit frequency
        self.freq = freq
        self.IF_freq = self.LO_freq-freq
        
    def set_offset_freq(self,offset):
        self.IF_freq += offset
        
    def set_LO_freq(self,freq):
        # sets qubit LO frequency
        self.LO_freq = freq
        self.IF_freq = freq-self.freq
        
    def set_pi_amp(self,amp): self.pi_amp = amp # sets pi-amp
    
    def set_half_pi_amp(self,amp): self.half_pi_amp = amp # sets half pi-amp
    
    def set_pi_dur(self,dur): self.pi_dur = dur # sets pi-pulse duration
        
    def set_mixer_IQ(self,mixer_IQ): # sets IQ-calibration
        
        self.I = mixer_IQ[0]
        self.Q = mixer_IQ[1]
        
        
class Sequence:
    
    # this class defines a pulse sequence for a given qubit
    # it is initiated by a qubit object
    
    def __init__(self,qubit):
        
        self.sampling_rate = 2.4e9 # in Hz         # sampling rate of an AWG generator
        self.q = qubit # instance of qubit class
        
        # new waveforms
        self.wave_length_drive = np.ceil(self.sampling_rate*4*self.q.pi_dur)
        if self.wave_length_drive%16 != 0:
            self.wave_length_drive = self.wave_length_drive+16-self.wave_length_drive%16
        
        self.t = np.linspace(0,(self.wave_length_drive-1)/self.sampling_rate, int(self.wave_length_drive))

        self.pi_envelope = np.exp(-((self.t - 2*self.q.pi_dur)/self.q.pi_dur)**4/2)
        # for tests
        # self.pi_envelope = np.ones(len(self.t))
        self.left_front = np.exp(-((self.t - 2*self.q.pi_dur)/self.q.pi_dur)**4/2)[0:len(self.pi_envelope)//2]
        self.right_front = np.exp(-((self.t - 2*self.q.pi_dur)/self.q.pi_dur)**4/2)[len(self.pi_envelope)//2:]
        
        #define gaussian pi-pulse envelope and its left and right fronts
        #the latter are used to smooth the rectangular drives
#         self.pi_envelope=np.exp(-np.linspace(-4,4,int(4*self.q.pi_dur*self.sampling_rate))**2/2)
#         self.left_front =np.exp(-np.linspace(-4,0,int(2*self.q.pi_dur*self.sampling_rate))**2/2)
#         self.right_front=np.exp(-np.linspace(0,4,int(2*self.q.pi_dur*self.sampling_rate))**2/2)
        
        self.phase_reference = 0   # phase reference used to take into account a virtual Z-rotation
        self.phases   = []         # phase shifts of the intermediate modulation of the pulse 
        self.freqs    = []         # intermediate frequencies of the pulses
        self.waves    = []         # pulses envelopes
        self.mixer_IQ = []         # IQ calibration parameters
        
        
        
    def addU2(self,theta,phi):
        
        #inserts the U2-rotation.  
        
        self.waves.append(self.q.pi_amp*theta*self.pi_envelope)
        self.freqs.append(self.q.IF_freq)
        self.phases.append(phi+self.phase_reference)
        self.mixer_IQ.append((self.q.I,self.q.Q))
        
    def addU2_half_pi(self,theta,phi):
        
        #inserts the U2-rotation.  
        
        self.waves.append(self.q.half_pi_amp*theta*self.pi_envelope)
        self.freqs.append(self.q.IF_freq)
        self.phases.append(phi+self.phase_reference)
        self.mixer_IQ.append((self.q.I,self.q.Q))
        
    def wait_points(self,points):
        
        self.waves.append(np.zeros(points))
        self.phases.append(0)
        self.freqs.append(0)
        self.mixer_IQ.append((0,0))
        
    def wait(self,duration):
    
        self.waves.append(np.zeros(int(self.sampling_rate*duration)))
        self.phases.append(0)
        self.freqs.append(0)
        self.mixer_IQ.append((0,0))
        
        
    def addCR(self,amp,dur,if_freq,phi,mixer_IQ):
        
        env =  list(self.left_front)
        env += list(np.ones(int(dur*self.sampling_rate)))
        env += list(self.right_front)
        
        self.waves.append(amp*np.asarray(env))
        self.freqs.append(if_freq)
        self.phases.append(phi)
        self.mixer_IQ.append(mixer_IQ)
        
    def addUZ(self,phi): self.phase_reference -=phi
        
    def get_waveforms(self):
        
        waveI=[]
        waveQ=[]
        
        seq_size = np.sum([len(xx) for xx in self.waves])
        
        time_index = 0
        
        for xx,yy,zz,ww in zip(self.waves,self.phases,self.freqs,self.mixer_IQ):
            
            tt=np.linspace(time_index,time_index+len(xx),len(xx),endpoint=False)/self.sampling_rate
            time_index += len(xx)
            
            waveI = waveI+list(xx*np.real(ww[0]*np.exp(2*np.pi*1j*zz*tt+1j*yy)))
            waveQ = waveQ+list(xx*np.imag(ww[1]*np.exp(2*np.pi*1j*zz*tt+1j*yy)))
            
        return waveI,waveQ
        
    def set_sampling_rate(self,rate): self.sampling_rate = rate
    
    def get_seq_length(self):
    
        return np.sum([int(len(xx)) for xx in self.waves])
        


class QCircuit:
    """
    __init__: number of qubits to be measureds
    """
    def __init__(self,nqubits):
        
        self.sequences={}
        self.connectivity={}
        self.nqubits=nqubits
        
    def set_rzx_connectivity(self,amp,dur,control,target,mixer_IQ):
        
        key = str(control)+str(target)
        
        self.connectivity[key]={}
        self.connectivity[key]['amp']  = amp
        self.connectivity[key]['dur']  = dur
        self.connectivity[key]['freq'] = self.sequences[target].q.IF_freq
        self.connectivity[key]['IQ']   = mixer_IQ
        
    def set_rzx_phase(self,control,target,phase):
    
        key = str(control)+str(target)
        self.connectivity[key]['phase']=phase
        
    def idle(self):
    
        return max([xx.get_seq_length() for xx in self.sequences])
                
    def set_qubit(self,nn,q): self.sequences[nn]=Sequence(q)
        
    def rx(self,theta,nn,phase = 0): 
        self.sequences[nn].addU2(theta,phase)
        
    def rx_half_pi(self,theta,nn,phase = 0): 
        self.sequences[nn].addU2_half_pi(theta,phase)
        
    def ry(self,theta,nn,phase=0): 
        self.sequences[nn].addU2(theta,np.pi/2+phase)
        
    def ry_half_pi(self,theta,nn,phase=0): 
        self.sequences[nn].addU2_half_pi(theta,np.pi/2+phase)
        
    def rz(self,phi,nn):   self.sequences[nn].addUZ(phi)
    
    def wait(self,duration,nn): self.sequences[nn].wait(duration)
    
    def u2(self,theta,phase,nn): self.sequences[nn].addU2(theta,phase)
    
    def rw(self,theta,angle,nn,phase=0): 
        self.sequences[nn].addU2(theta,angle+phase)
        
    def cx(self,control,target):
        
        key = str(control)+str(target)
        
        if key in self.connectivity.keys():
                   
            self.sequences[control].addU2(1.0,np.pi)
            self.sequences[target].addU2(0.5,np.pi)
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
                                          self.connectivity[key]['dur']/2,
                                          self.connectivity[key]['freq'],
                                          self.sequences[target].phase_reference,  
                                          self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addU2(1.0,np.pi/2)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
                                          self.connectivity[key]['dur']/2,
                                          self.connectivity[key]['freq'],
                                          np.pi + self.sequences[target].phase_reference,
                                          self.connectivity[key]['IQ'])
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addUZ(-np.pi/2)
            
        else:
        
           print('No connectivity for a two-qubit gate')
            
    def rzx_0(self,control,target,phase=0,phase_offset=0,offset_freq = 0):
        
        key = str(control)+str(target)
        
        if key in self.connectivity.keys():
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
                                          self.connectivity[key]['dur']/2,
                                          self.connectivity[key]['freq']+offset_freq,
                                          self.sequences[target].phase_reference-phase,  
                                          self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addU2(1.0,0)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
                                          self.connectivity[key]['dur']/2,
                                          self.connectivity[key]['freq']+offset_freq,
                                          np.pi + self.sequences[target].phase_reference+phase_offset-phase,
                                          self.connectivity[key]['IQ'])
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addU2(1.0,0)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
        else:
            
            print('No connectivity for a two-qubit gate')
            
    
            
    def rzx_1(self,control,target,phase=0,phase_offset=0,offset_freq = 0):
        
        key = str(control)+str(target)
        
        if key in self.connectivity.keys():
        
            self.sequences[control].addU2(1.0,0)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
                                          self.connectivity[key]['dur']/2,
                                          self.connectivity[key]['freq']+offset_freq,
                                          self.sequences[target].phase_reference-phase,  
                                          self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addU2(1.0,0)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
                                          self.connectivity[key]['dur']/2,
                                          self.connectivity[key]['freq']+offset_freq,
                                          np.pi + self.sequences[target].phase_reference+phase_offset-phase,
                                          self.connectivity[key]['IQ'])
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            
            
        else:
            
            print('No connectivity for a two-qubit gate')
            
    def cr0(self,control,target,amp,dur,phase=0):
        
        key = str(control)+str(target)
        
        if key in self.connectivity.keys():
            
            self.sequences[control].addCR(amp,
                                          dur,
                                          self.connectivity[key]['freq'],
                                          self.sequences[target].phase_reference-phase,  
                                          self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
        else:
            
            print('No connectivity for a two-qubit gate')
            
            
    def cr1(self,control,target,amp,dur):
        
        key = str(control)+str(target)
        
        if key in self.connectivity.keys():
        
            self.sequences[control].addU2(1.0,0)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addCR(amp,
                                          dur,
                                          self.connectivity[key]['freq'],
                                          self.sequences[target].phase_reference,  
                                          self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
        else:
            
            print('No connectivity for a two-qubit gate')
            
    def rzx(self,control,target,phase=0):
        
        key = str(control)+str(target)
        
        if key in self.connectivity.keys():
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],
            self.connectivity[key]['dur']/2,                 
            self.connectivity[key]['freq'],                       self.sequences[target].phase_reference-self.connectivity[key]['phase']-phase,         
            self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addU2(1.0,0)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addCR(self.connectivity[key]['amp'],self.connectivity[key]['dur']/2,               self.connectivity[key]['freq'],np.pi + self.sequences[target].phase_reference-self.connectivity[key]['phase']-phase, self.connectivity[key]['IQ'])
            
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
            self.sequences[control].addU2(1.0,np.pi)
            self.sequences[target].wait_points(len(self.sequences[control].waves[-1]))
            
        else:
            
            print('No connectivity for a two-qubit gate')
            
        
    def get_waveforms(self,nn):
        
        return self.sequences[nn].get_waveforms()
        
    def get_pi_duration(self,nn):
    
        return self.sequences[nn].q.pi_dur
        