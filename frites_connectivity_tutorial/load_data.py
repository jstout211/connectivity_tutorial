#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 11:09:54 2022

@author: jstout
"""

import mne
from frites.dataset import DatasetEphy
import glob
import pandas as pd
import os
from scipy.io import loadmat
import numpy as np

# =============================================================================
# 
# =============================================================================
def load_mnedata(frites_output_root):
    '''Return list of MNE source epochs'''
    x_mne = []
    epoch_files = glob.glob(frites_output_root+ '/*_epo.fif')
    sorted(epoch_files)
    for k in epoch_files:
        epoch = mne.read_epochs(k)
        # finally, replace it in the original list
        x_mne.append(epoch)
    return x_mne

def renameROI(rois):
    
    '''rename the roi names inside the rois list
    input       output
    name-Xh --> X_name'''
    
    roiList = []
    for roi in rois:
        if not roi == 'ROInames':
            tmp_ = roi.split('-')
            if tmp_[-1] == 'lh':
                roiList.append('L_' + tmp_[0])
            else:
                roiList.append('R_'+ tmp_[0])

    return roiList

def load_dataset(frites_output_root):
    '''Load the MNE data, convert, and return EphysDataset'''
    x_mne = load_mnedata(frites_output_root)
    labels_fname = os.path.join(frites_output_root, 'ROIs_DK.csv')
    #Save out the roi names if not done
    #pd.DataFrame(label_names, columns=['ROInames']).to_csv(labels_fname,index=False)
    rois = pd.read_csv(labels_fname).ROInames.tolist()
    rois = renameROI(rois) # frites friendly format
    
    times_fname = os.path.join(frites_output_root, 'Epoch_times.csv')
    #pd.DataFrame(epoch.times, columns=['Times']).to_csv(times_fname,index=False)
    times = pd.read_csv(times_fname).Times.tolist()
    
    dt = DatasetEphy(x_mne, 
                     y = [tmp_.events[:,2] for tmp_ in x_mne],
                     roi=[rois for i in range(len(x_mne))],
                     times=times)
    return dt


def matToxArray(mat_fname):

    ''' load .mat file containing electrophysio/meg data and convert it to xArray format'''

    dict_ = loadmat(mat_fname) # dictionary
            
    data = dict_['data'].astype(int) # sampled at 1000Hz, scale factor: 1 amplifier unit = .0298 microvolts; built-in band pass 0.15 to 200 Hz, 
    cues = dict_['cues'].astype(int) # Timing of visual cues to read noun or produce associated verb. 

    # These files also contain information about electrocortical stimulation (ECS). 
    stimSites = dict_['stimsites'].astype(int).flatten() # N” channels which were stimulated as part of a stimulation pair
    ecssites = dict_['ecssites'].astype(int) # Channel pairs where ECS produced interruption of naming during clinical mapping.


    # make epochs from current data
    chanNames = ['Electrode_' + str(el+1) for el in range(data.shape[1])] 
    ch_types = ['ecog']*len(chanNames)
    sfreq= 1000
    info = mne.create_info(chanNames, ch_types=ch_types, sfreq=sfreq)

    # sensor position is contained in mainPath/brains/xx_brain.mat
    raw = mne.io.RawArray(data.T,info)

    peaks0 = np.where(cues.flatten()>=.5)[0]
    onsets = (np.append(peaks0[0],peaks0[np.where(np.diff(peaks0)>1)[0]+1])) 
    offsets = (np.append(peaks0[np.where(np.diff(peaks0)>1)[0]]-1,peaks0[-1])) 

    '''
    fig, ax=plt.subplots()
    ax.plot(cues.flatten(), alpha=0.5)
    for nn in range(len(offsets)):
        ax.vlines(onsets[nn],0,1,color='tab:Green',lw=1.5, alpha=0.5 )
        ax.vlines(offsets[nn],0,1,color='red',lw=1.5, alpha=0.5 )
        #ax.scatter(offset[nn],4.897,marker = 'x', color='red')
    plt.show(block=False)
    '''

    # make event matrix
    ids = ([1,2])*len(onsets)
    trials = np.concatenate((onsets,offsets)).reshape(2,len(onsets)).T.flatten()
    events = np.zeros([len(trials),3])
    events[:,0] = trials
    events[:,-1] = ids

    tDur = 1.6 # task duration - extracted from paper
    epochs = mne.Epochs(raw, events.astype(int), event_id=1, tmin=-0.5, tmax=0.8+tDur, baseline=(-.5, 0))


    ## @@@ TODO -- ROIS?
    dt = DatasetEphy(epochs, 
                     y = [tmp_.events[:,2] for tmp_ in epochs],
                     roi=[rois for i in range(len(epochs))],
                     times=epochs.times)