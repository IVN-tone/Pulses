from libs.waveforms_constructor import *
# 'range_q' changed 'wf_scaling' (except 4Q methods) 02.23

def calibration_wfs_ground(qubits_params, mixer_cals, LO_q):    
    q_cal=qubit(qubits_params['drive_q'], qubits_params['drive_res'])
    q_cal.set_pi_amp(qubits_params['pi_amp']*qubits_params['wf_scaling']*qubits_params['range_q'])
    q_cal.set_pi_dur(qubits_params['td']*1e-9)
    q_cal.set_LO_freq(LO_q)
    q_cal.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])

    qc_cal=QCircuit(1)
    qc_cal.set_qubit(0,q_cal) # uploads waveform, classes: QCircuit, Sequence
    qc_cal.rx(0,0)
    
    return qc_cal.get_waveforms(0)

def calibration_wfs_excited(qubits_params, mixer_cals, LO_q, osc=False):    
    q_cal=qubit(qubits_params['drive_q'], qubits_params['drive_res'])
    q_cal.set_pi_amp(qubits_params['pi_amp']*qubits_params['wf_scaling']*qubits_params['range_q'])
    q_cal.set_pi_dur(qubits_params['td']*1e-9)
    q_cal.set_LO_freq(LO_q)
    # without internal oscillator
    q_cal.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])
    
    if osc:
        q_cal.set_LO_freq(qubits_params['drive_q'])
        # with internal oscillator
        q_cal.set_mixer_IQ([0.4, 1j*abs(mixer_cals[0]+mixer_cals[1]*1j)])
    

    qc_cal=QCircuit(1)
    qc_cal.set_qubit(0,q_cal) # uploads waveform, classes: QCircuit, Sequence
    qc_cal.rx(1,0)
    
    return qc_cal.get_waveforms(0)
    
def calibration_wfs_excited_12(qubits_params, mixer_cals, LO_q):
    q_cal=qubit(qubits_params['drive_q_12'], qubits_params['drive_res'])
    q_cal.set_pi_amp(qubits_params['pi_amp_12']*qubits_params['wf_scaling']*qubits_params['range_q'])
    q_cal.set_pi_dur(qubits_params['td']*1e-9)
    q_cal.set_LO_freq(LO_q)
    q_cal.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])

    qc_cal=QCircuit(1)
    qc_cal.set_qubit(0,q_cal) # uploads waveform, classes: QCircuit, Sequence
    qc_cal.rx(1,0)
    
    return qc_cal.get_waveforms(0)
    
def pi_pulses_amp_sweep(qubits_params, mixer_cals, LO_q, num_pi_pulses):    
    q_cal=qubit(qubits_params['drive_q'], qubits_params['drive_res'])
    q_cal.set_pi_amp(qubits_params['pi_amp']*qubits_params['wf_scaling'])
    q_cal.set_pi_dur(qubits_params['td']*1e-9)
    q_cal.set_LO_freq(LO_q)
    q_cal.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])

    qc_cal=QCircuit(1)
    qc_cal.set_qubit(0,q_cal) # uploads waveform, classes: QCircuit, Sequence
    for i in range(num_pi_pulses):
        qc_cal.rx(1,0)
    
    return qc_cal.get_waveforms(0)
    
def half_pi_pulses_amp_sweep(qubits_params, mixer_cals, LO_q, num_half_pi_pulses):    
    q_cal=qubit(qubits_params['drive_q'], qubits_params['drive_res'])
    q_cal.set_half_pi_amp(qubits_params['half_pi_amp']*qubits_params['wf_scaling'])
    q_cal.set_pi_dur(qubits_params['td']*1e-9)
    q_cal.set_LO_freq(LO_q)
    q_cal.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])

    qc_cal=QCircuit(1)
    qc_cal.set_qubit(0,q_cal) # uploads waveform, classes: QCircuit, Sequence
    for i in range(num_half_pi_pulses):
        qc_cal.rx_half_pi(1,0)
    
    return qc_cal.get_waveforms(0)
    
def calibration_ground_4Q(qubits_params, mixer_cals, LO_q):
    mixer_vector1 = mixer_cals[1]['RF_q'].tolist()[0]+mixer_cals[1]['RF_q'].tolist()[1]*1j
    mixer_vector2 = mixer_cals[2]['RF_q'].tolist()[0]+mixer_cals[2]['RF_q'].tolist()[1]*1j
    mixer_vector3 = mixer_cals[3]['RF_q'].tolist()[0]+mixer_cals[3]['RF_q'].tolist()[1]*1j
    mixer_vector4 = mixer_cals[4]['RF_q'].tolist()[0]+mixer_cals[4]['RF_q'].tolist()[1]*1j
    
    q1=qubit(qubits_params[1]['drive_q'], qubits_params[1]['drive_res'])
    q2=qubit(qubits_params[2]['drive_q'], qubits_params[2]['drive_res'])
    q3=qubit(qubits_params[3]['drive_q'], qubits_params[3]['drive_res'])
    q4=qubit(qubits_params[4]['drive_q'], qubits_params[4]['drive_res'])

    for q,ii in zip([q1,q2,q3,q4],[1,2,3,4]):
        q.set_pi_amp(qubits_params[ii]['pi_amp']*qubits_params[ii]['range_q'])
        q.set_pi_dur(qubits_params[ii]['td']*1e-9)
        q.set_LO_freq(LO_q)
        q.set_mixer_IQ([0.4, eval('mixer_vector'+str(ii))])   
    
    qc=QCircuit(4)
    qc.set_qubit(0,q1)
    qc.set_qubit(1,q2)
    qc.set_qubit(2,q3)
    qc.set_qubit(3,q4)

    qc.rx(0.0,0)
    qc.rx(0.0,1)
    qc.rx(0.0,2)
    qc.rx(0.0,3)
    
    waveforms = {}
    for i in range(4):
        waveforms['I'+str(i)] = qc.get_waveforms(i)[:][0]
        waveforms['Q'+str(i)] = qc.get_waveforms(i)[:][1]
    return waveforms['I0'], waveforms['Q0'], waveforms['I1'], waveforms['Q1'], waveforms['I2'], waveforms['Q2'], waveforms['I3'], waveforms['Q3']
    
def calibration_excited_4Q(qubits_params, mixer_cals, LO_q):
    mixer_vector1 = mixer_cals[1]['RF_q'].tolist()[0]+mixer_cals[1]['RF_q'].tolist()[1]*1j
    mixer_vector2 = mixer_cals[2]['RF_q'].tolist()[0]+mixer_cals[2]['RF_q'].tolist()[1]*1j
    mixer_vector3 = mixer_cals[3]['RF_q'].tolist()[0]+mixer_cals[3]['RF_q'].tolist()[1]*1j
    mixer_vector4 = mixer_cals[4]['RF_q'].tolist()[0]+mixer_cals[4]['RF_q'].tolist()[1]*1j
    
    q1=qubit(qubits_params[1]['drive_q'], qubits_params[1]['drive_res'])
    q2=qubit(qubits_params[2]['drive_q'], qubits_params[2]['drive_res'])
    q3=qubit(qubits_params[3]['drive_q'], qubits_params[3]['drive_res'])
    q4=qubit(qubits_params[4]['drive_q'], qubits_params[4]['drive_res'])

    for q,ii in zip([q1,q2,q3,q4],[1,2,3,4]):
        q.set_pi_amp(qubits_params[ii]['pi_amp']*qubits_params[ii]['range_q'])
        q.set_pi_dur(qubits_params[ii]['td']*1e-9)
        q.set_LO_freq(LO_q)
        q.set_mixer_IQ([0.4, eval('mixer_vector'+str(ii))])   
    
    qc=QCircuit(4)
    qc.set_qubit(0,q1)
    qc.set_qubit(1,q2)
    qc.set_qubit(2,q3)
    qc.set_qubit(3,q4)

    qc.rx(1.0,0)
    qc.rx(1.0,1)
    qc.rx(1.0,2)
    qc.rx(1.0,3)
    
    waveforms = {}
    for i in range(4):
        waveforms['I'+str(i)] = qc.get_waveforms(i)[:][0]
        waveforms['Q'+str(i)] = qc.get_waveforms(i)[:][1]
    return waveforms['I0'], waveforms['Q0'], waveforms['I1'], waveforms['Q1'], waveforms['I2'], waveforms['Q2'], waveforms['I3'], waveforms['Q3']
    
def calibration_4Q(qubits_params, mixer_cals, LO_q, state):
    mixer_vector1 = mixer_cals[1]['RF_q'].tolist()[0]+mixer_cals[1]['RF_q'].tolist()[1]*1j
    mixer_vector2 = mixer_cals[2]['RF_q'].tolist()[0]+mixer_cals[2]['RF_q'].tolist()[1]*1j
    mixer_vector3 = mixer_cals[3]['RF_q'].tolist()[0]+mixer_cals[3]['RF_q'].tolist()[1]*1j
    mixer_vector4 = mixer_cals[4]['RF_q'].tolist()[0]+mixer_cals[4]['RF_q'].tolist()[1]*1j
    
    q1=qubit(qubits_params[1]['drive_q'], qubits_params[1]['drive_res'])
    q2=qubit(qubits_params[2]['drive_q'], qubits_params[2]['drive_res'])
    q3=qubit(qubits_params[3]['drive_q'], qubits_params[3]['drive_res'])
    q4=qubit(qubits_params[4]['drive_q'], qubits_params[4]['drive_res'])

    for q,ii in zip([q1,q2,q3,q4],[1,2,3,4]):
        q.set_pi_amp(qubits_params[ii]['pi_amp']*qubits_params[ii]['range_q'])
        q.set_pi_dur(qubits_params[ii]['td']*1e-9)
        q.set_LO_freq(LO_q)
        q.set_mixer_IQ([0.4, eval('mixer_vector'+str(ii))])   
    
    qc=QCircuit(4)
    qc.set_qubit(0,q1)
    qc.set_qubit(1,q2)
    qc.set_qubit(2,q3)
    qc.set_qubit(3,q4)
    
    if state=='0000':
        qc.rx(0.0,0)
        qc.rx(0.0,1)
        qc.rx(0.0,2)
        qc.rx(0.0,3)
    elif state=='1111':
        qc.rx(1.0,0)
        qc.rx(1.0,1)
        qc.rx(1.0,2)
        qc.rx(1.0,3)
    
    waveforms = {}
    for i in range(4):
        waveforms['I'+str(i)] = qc.get_waveforms(i)[:][0]
        waveforms['Q'+str(i)] = qc.get_waveforms(i)[:][1]
    return [waveforms['I0']], [waveforms['Q0']], [waveforms['I1']], [waveforms['Q1']], [waveforms['I2']], [waveforms['Q2']], [waveforms['I3']], [waveforms['Q3']]
    
def calibration_16_states_4Q(qubits_params, mixer_cals, LO_q, state):
    mixer_vector1 = mixer_cals[1]['RF_q'].tolist()[0]+mixer_cals[1]['RF_q'].tolist()[1]*1j
    mixer_vector2 = mixer_cals[2]['RF_q'].tolist()[0]+mixer_cals[2]['RF_q'].tolist()[1]*1j
    mixer_vector3 = mixer_cals[3]['RF_q'].tolist()[0]+mixer_cals[3]['RF_q'].tolist()[1]*1j
    mixer_vector4 = mixer_cals[4]['RF_q'].tolist()[0]+mixer_cals[4]['RF_q'].tolist()[1]*1j
    
    q1=qubit(qubits_params[1]['drive_q'], qubits_params[1]['drive_res'])
    q2=qubit(qubits_params[2]['drive_q'], qubits_params[2]['drive_res'])
    q3=qubit(qubits_params[3]['drive_q'], qubits_params[3]['drive_res'])
    q4=qubit(qubits_params[4]['drive_q'], qubits_params[4]['drive_res'])

    for q,ii in zip([q1,q2,q3,q4],[1,2,3,4]):
        q.set_pi_amp(qubits_params[ii]['pi_amp']*qubits_params[ii]['range_q'])
        q.set_pi_dur(qubits_params[ii]['td']*1e-9)
        q.set_LO_freq(LO_q)
        q.set_mixer_IQ([0.4, eval('mixer_vector'+str(ii))])   
    
    qc=QCircuit(4)
    qc.set_qubit(0,q1)
    qc.set_qubit(1,q2)
    qc.set_qubit(2,q3)
    qc.set_qubit(3,q4)
    
    for i,j in enumerate(state):
        qc.rx(int(j),i)  
        
    
    waveforms = {}
    for i in range(4):
        waveforms['I'+str(i)] = qc.get_waveforms(i)[:][0]
        waveforms['Q'+str(i)] = qc.get_waveforms(i)[:][1]
    return [waveforms['I0']], [waveforms['Q0']], [waveforms['I1']], [waveforms['Q1']], [waveforms['I2']], [waveforms['Q2']], [waveforms['I3']], [waveforms['Q3']]
    
def generate_ramsey_wfs(qubits_params, mixer_cals, LO_q, delay, offset):
    # initialization
    q1=qubit(qubits_params['drive_q'], qubits_params['drive_res'])
    q1.set_pi_amp(qubits_params['pi_amp']*qubits_params['wf_scaling']*qubits_params['range_q'])
    q1.set_pi_dur(qubits_params['td']*1e-9)
    q1.set_LO_freq(LO_q)
    q1.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])
    q1.set_offset_freq(offset)
    
    # ramsey sequence
    qc=QCircuit(1)
    qc.set_qubit(0,q1)
    
    qc.rx(1/2,0)
    qc.wait(delay,0)
    qc.rx(1/2,0)
    
    return qc.get_waveforms(0)
    
def pi_pulses_frequency_sweep(qubits_params, mixer_cals, LO_q, offset, num_pi_pulses):
    # initialization
    q1=qubit(qubits_params['drive_q'], qubits_params['drive_res'])
    q1.set_pi_amp(qubits_params['pi_amp']*qubits_params['wf_scaling'])
    q1.set_pi_dur(qubits_params['td']*1e-9)
    q1.set_LO_freq(LO_q)
    q1.set_mixer_IQ([0.4, mixer_cals[0]+mixer_cals[1]*1j])
    q1.set_offset_freq(offset)
    
    # ramsey sequence
    qc=QCircuit(1)
    qc.set_qubit(0,q1)
    
    for i in range(num_pi_pulses):
        qc.rx(1,0)
        qc.rx(-1,0)
    
    return qc.get_waveforms(0)