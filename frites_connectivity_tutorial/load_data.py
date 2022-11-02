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


