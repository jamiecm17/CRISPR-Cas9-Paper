"""
Created on Wed Feb  2 10:08:25 2022

@author: moffa
"""
def evoked_VP(abf_file,output_file,pulse_n=1,sample_rate=20000):
    import pyabf
    import numpy as np
    from scipy import signal
    import matplotlib.pyplot as plt
    import pandas as pd
#Import abf files using pyabf.ABF and save as variables
    abf=pyabf.ABF(abf_file)
#Determine number of sweeps in files
    sweep=abf.sweepCount
#get sweep timestamps
    abf.setSweep(0)
    time=abf.sweepX
#initialize matrix for sweep data and pulse times
    mat=np.empty((sweep+1,len(time)))
    mat[0,:]=time
    pulse_idx=np.empty((sweep,pulse_n))
#get baseline-adjusted sweep data
    for i in range(sweep):
        epoch=abf.sweepEpochs.p1s
        for n in range(pulse_n):
            pulse_idx[i,n]=int(epoch[2*(n+1)]) #in epoch, pulses are always even indices from [2,end)
        pulse_idx=pulse_idx.astype(int)
        abf.setSweep(i,baseline=[.1,.15])
        mat[i+1,:]=abf.sweepY
#Produce lowpass-filtered data for analysis
    matLow=np.empty((sweep,len(time)))
    b,a=signal.butter(3,100,'low',fs=sample_rate)
    for i in range(sweep):
        matLow[i,:]=signal.lfilter(b,a,mat[i+1,:])
#get trace data (peak, peak index after pulse onset, peak index from start of sweep, 10ms before peak, 10ms after peak, 20 ms average around peak).
    stats=np.empty((sweep,6*pulse_n))
    for i in range(sweep):
        epoch=abf.sweepEpochs.p1s
        for n in range(pulse_n):
            end_idx=epoch[(2*(n+1))+2]
            stats[i,(0+(n*6))]=max(mat[i+1,3000:6000])
            if np.size(np.where(mat[i+1,3000:6000]==stats[i,(0+(n*6))])[0])==0:
                stats[i,(1+(n*6))]=np.where(mat[i+1,3000:6000]==-stats[i,(0+(n*6))])[0][0]
            else:
                stats[i,(1+(n*6))]=np.where(mat[i+1,3000:6000]==stats[i,(0+(n*6))])[0][0]
            stats[i,(2+(n*6))]=stats[i,(1+(n*6))]+1500
            stats[i,(3+(n*6))]=int(stats[i,(2+(n*6))]-10)
            stats[i,(4+(n*6))]=int(stats[i,(2+(n*6))]+10)
            stats[i,(5+(n*6))]=np.mean(mat[i+1,int(stats[i,(3+(n*6))]):int(stats[i,(4+(n*6))])]) #average of 20 frames surrounding the max value
#get average 
    mean=np.mean(mat[1:sweep+1,:],axis=0)
    out=(mat,mean,stats)
#export data to excel
    statsdf=pd.DataFrame(stats,columns=['Peak Value (pA)','Peak Index (after Pulse)','Peak Index (after sweep onset)','10 ms before peak','10 ms after peak','20 ms average (pA)'])
    with pd.ExcelWriter(output_file,engine="openpyxl",mode="a") as writer:
        statsdf.to_excel(writer)

#plot IPSCs
    plt.figure()
    for i in range(sweep):
        plt.plot(time,mat[i+1,:],'b',alpha=.5)
    plt.plot(time,mean,'b',alpha=1,label='Average')
    plt.title('2022_01_06 IPSC Traces')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (pA)')
    plt.legend()
    return out

def evoked_NAc(abf_file,output_file,pulse_n=1,sample_rate=20000):
    import pyabf
    import numpy as np
    from scipy import signal
    import matplotlib.pyplot as plt
    import pandas as pd
#Import abf files using pyabf.ABF and save as variables
    abf=pyabf.ABF(abf_file)
#Determine number of sweeps in files
    sweep=abf.sweepCount
#get sweep timestamps
    abf.setSweep(0)
    time=abf.sweepX
#initialize matrix for sweep data and pulse times
    mat=np.empty((sweep+1,len(time)))
    mat[0,:]=time
    pulse_idx=np.empty((sweep,pulse_n))
#get baseline-adjusted sweep data
    for i in range(sweep):
        epoch=abf.sweepEpochs.p1s
        for n in range(pulse_n):
            pulse_idx[i,n]=int(epoch[2*(n+1)]) #in epoch, pulses are always even indices from [2,end)
        pulse_idx=pulse_idx.astype(int)
        abf.setSweep(i,baseline=[.1,.15])
        mat[i+1,:]=abf.sweepY
#Produce lowpass-filtered data for analysis
    matLow=np.empty((sweep,len(time)))
    b,a=signal.butter(3,100,'low',fs=sample_rate)
    for i in range(sweep):
        matLow[i,:]=signal.lfilter(b,a,mat[i+1,:])
#get trace data #get trace data (peak, 10% value, 10% time=latency, 90% value, 90% time, rise time). 10% and 90% times are reported as time since pulse onset
    stats=np.empty((sweep,6*pulse_n))
    for i in range(sweep):
        epoch=abf.sweepEpochs.p1s
        for n in range(pulse_n):
            end_idx=epoch[(2*(n+1))+2]
            stats[i,(0+(n*6))]=max(mat[i+1,3000:6000]) #peak evoked current
            stats[i,(1+(n*6))]=0.1*stats[i,(0+(n*6))] #10% value of peak
            stats[i,(2+(n*6))]=np.where(mat[i+1,3000:6000]>=stats[i,(1+(n*6))])[0][0] #10% time (latency)
            stats[i,(3+(n*6))]=0.9*stats[i,(0+(n*6))] #90% value of peak
            stats[i,(4+(n*6))]=np.where(mat[i+1,3000:6000]>=stats[i,(3+(n*6))])[0][0] #90% time
            stats[i,(5+(n*6))]=stats[i,(4+(n*6))]-stats[i,(2+(n*6))] #rise time (90%-10%)
#get average 
    mean=np.mean(mat[1:sweep+1,:],axis=0)
    out=(mat,mean,stats)
#export data to excel
    statsdf=pd.DataFrame(stats,columns=['Peak Value (pA)','10% Value (pA)','Latency (s)','90% Value (pA)','90% Time (s)','Rise Time (s)'])
    with pd.ExcelWriter(output_file,engine="openpyxl",mode="a") as writer:
        statsdf.to_excel(writer)

#plot IPSCs
    plt.figure()
    for i in range(sweep):
        plt.plot(time,mat[i+1,:],'b',alpha=.5)
    plt.plot(time,mean,'b',alpha=1,label='Average')
    plt.title('2022_01_06 IPSC Traces')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (pA)')
    plt.legend()
    return out

def abf_Reader_VP(directory):
    import os
    from evoked_all import evoked_VP
    os.chdir(directory)
    out=[]
    for file in os.listdir(directory):
        data=evoked_VP(file)
        out.append(data)
    return out

def abf_Reader_NAc(directory):
    import os
    from evoked_all import evoked_NAc
    os.chdir(directory)
    out=[]
    for file in os.listdir(directory):
        data=evoked_NAc(file)
        out.append(data)
    return out