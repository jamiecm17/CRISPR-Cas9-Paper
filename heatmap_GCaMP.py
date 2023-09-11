"""
Created on Tue Apr 25 13:12:14 2023

@author: moffa
"""
#convert csv files to format usable by guppy
def guppy_Fmt(csv,output_file_gcamp,output_file_rewtime,output_file_cuetime):
    import pandas as pd
    import numpy as np
    #import csv data and read into pandas dataframe
    data=pd.read_csv(csv)
    ndata=data.to_numpy()
    ts=ndata[:,0]-ndata[0,0]
    signal=ndata[:,1]
    gdata={'timestamps':ts,'data':signal}
    gdf=pd.DataFrame(gdata)
    #extract events (cue and reward)
    events=[]
    for i in range(len(ndata[:,2])):
        if ndata[i-1,2]==False:
            if ndata[i,2]==True:
                events.append(ts[i])
    #extract reward events (in this system, 1 pulse was output for reward, 2 for cue. So reward events always fell on integers divisible by 3)
    nom=[]
    for i in range(len(events)):
        if i%3==0:
            nom.append(events[i])
    #extract cue events (see above; cue events always fell on pulse integers with remainder=1 when divided by 3)
    beep=[]
    for i in range(len(events)):
        if i%3==1:
            beep.append(events[i])
   #get timestamps that correspond to the cue and reward event integers and convert to dataframe
    gnom={'timestamps':nom}
    gbeep={'timestamps':beep}
    gnome=pd.DataFrame(gnom)
    gbeepe=pd.DataFrame(gbeep)
    #output gcamp data, cue times, and reward times as csv files
    gdf.to_csv(output_file_gcamp,index=False)
    gnome.to_csv(output_file_rewtime,index=False)
    gbeepe.to_csv(output_file_cuetime,index=False)

#create heatmap from GCaMP8f data from all trials across all days for each mouse
def heatmap_GCaMP(csv,hdf5,ts_tone,ts_rwd,sample_rate,output_file_cue,output_file_reward):
   #import libraries
    import seaborn
    import pandas as pd
    import numpy as np
    import h5py
    import math
    import matplotlib.pyplot as plt
    #read files
    dff_data=h5py.File(hdf5)
    dff_dataset=dff_data['data']
    dff=[]
    for i in dff_dataset:
        dff.append(i)
    data=pd.read_csv(csv)
    time_tone=pd.read_csv(ts_tone)
    time_rwd=pd.read_csv(ts_rwd)
    #align timestamps to dff data
    time_align=np.where(data['timestamps']>1)
    timestamp=[]
    for i in time_align:
        timestamp.append(data['timestamps'][i])
    ts=[]
    for i in timestamp[0]:
        ts.append(i)
    align_data=np.zeros([2,len(ts)])
    align_data[0,:]=ts
    align_data[1,:]=dff
    #find indices for tone and reward times
    tone_idx=[]
    for i in range(len(time_tone['timestamps'])):
        ph=np.where(ts>time_tone['timestamps'][i])
        tone_idx.append(ph[0][0])
    rwd_idx=[]
    for i in range(len(time_rwd['timestamps'])):
        ph=np.where(ts>time_rwd['timestamps'][i])
        rwd_idx.append(ph[0][0])
    #capture data 2s before and 2s after tone/reward time
    tone_trials=np.zeros([len(tone_idx),math.ceil(sample_rate)*4])
    for i in range(len(tone_idx)):
        start_idx=tone_idx[i]-(math.ceil(sample_rate)*2)
        end_idx=tone_idx[i]+(math.ceil(sample_rate)*2)
        tone_trials[i,:]=align_data[1,start_idx:end_idx]
    rwd_trials=np.zeros([len(rwd_idx),math.ceil(sample_rate)*4])
    for i in range(len(tone_idx)):
        start_idx=rwd_idx[i]-(math.ceil(sample_rate)*2)
        end_idx=rwd_idx[i]+(math.ceil(sample_rate)*2)
        rwd_trials[i,:]=align_data[1,start_idx:end_idx]
    #make trial timestamps from -2s to 2s
    trial_time=np.arange(-2,2,1/math.ceil(sample_rate))
    trial_ts=[]
    for i in trial_time:
        trial_ts.append(i)
    #make trial data into a dataframe
    tone_df=pd.DataFrame(tone_trials,columns=trial_ts)
    rwd_df=pd.DataFrame(rwd_trials,columns=trial_ts)
    #export dataframes to csv
    tone_df.to_csv(output_file_cue,index=False)
    rwd_df.to_csv(output_file_reward,index=False)
    #make heatmaps centered on tone and reward for individual mice on individual days
    plt.figure(0)
    tone_heatmap=seaborn.heatmap(tone_df,vmin=-2,vmax=5,xticklabels=33)
    plt.title('Tone Heatmap')
    plt.xlabel('Time (s)')
    plt.ylabel('Trial')
    plt.figure(1) 
    rwd_heatmap=seaborn.heatmap(rwd_df,vmin=-2,vmax=5,xticklabels=33)
    plt.title('Reward Heatmap')
    plt.xlabel('Time (s)')
    plt.ylabel('Trial')
    return tone_heatmap,rwd_heatmap