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


def matToEpochs(mat_fname):

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
    
    # tmp_ = (cues[:-1]-cues[1:])*-1
    # onsets = np.where(tmp_==1)[0]
    # offsets = np.where(tmp_==-1)[0]
    

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
    return epochs

def load_basic_speech(topdir):
    import glob
    verbs=glob.glob(f'{topdir}/*verbs.mat')
    nouns=glob.glob(f'{topdir}/*nouns.mat')
    verb_subj_epos = []
    verb_chs=[]
    category_list = []

    for fname in verbs:
        epo = matToEpochs(fname)
        verb_subj_epos.append(epo.get_data())
        verb_chs.append(epo.ch_names)
        category_list.append([1]*len(epo))
    for fname in nouns:
        epo = matToEpochs(fname)
        verb_subj_epos.append(epo.get_data())
        verb_chs.append(epo.ch_names)
        category_list.append([2]*len(epo))
    
    dt = DatasetEphy(verb_subj_epos, 
                 # y = [1]*len(verb_subj_epos),
                 y = category_list,
                 roi=verb_chs,
                 times=epo.times)
    
    global subjIDs_ephy
    subjIDs_ephy = []
    
    allFiles = verbs + nouns
    for file in allFiles:
        subjIDs_ephy.append(file.split('/')[-1].split('_')[0])

    return dt
    

def add_head(renderer, points, triangles, color, opacity=0.95):
    
    ''' helper function for rendering '''
    renderer.mesh(*points.T, triangles=triangles, color=color,
                  opacity=opacity)       

def showElectrodes_speech(topdir, subjID):

    ''' 
    show electrode locations on the brain 

    input: 
    topdir: BASIC_SPEECH/data/
    subjID: subject number in xarray
    subjIDs_ephy: global variable - list containing all subject IDs that comprise the ephy object

    output:
    mne figure with head mesh and electrodes
    '''

    # find path to brain data and load them
    brainDataPath = os.path.realpath(os.path.join(topdir, '..', 'brains'))
    brains = glob.glob(f'{brainDataPath}/*brain.mat')

    # get subjIDs that have brain/electrode data
    subjIDs_brains = [brain.split('/')[-1].split('_')[0] for brain in brains]

    # get ID of selected subject in ephy object
    sel_subjID = subjIDs_ephy[subjID]
    try:
        idx = subjIDs_brains.index(sel_subjID) # if it exists, find brain data of the selected subject
        fname = brains[idx]
        dict_ = loadmat(fname)

        print('loading data from subject ' + sel_subjID)

        brain = dict_['brain'] # brain mesh vertex/faces
        rr = brain[0][0][0] # coordinates
        tris = brain[0][0][1] - 1 # triangles - they are one based, make them  0 based

        locs = dict_['locs'] # electrode locations

        # create mne renderer to plot data 
        renderer = mne.viz.backends.renderer.create_3d_figure(
            size=(600, 600), bgcolor='w', scene=False)

        # render brain mesh
        add_head(renderer, rr,tris, color='gray',opacity=0.5)

        # render electrode locations and label
        for l in range(locs.shape[0]):

            renderer.sphere(center=locs[l,:], color='yellow', scale=2)
            renderer.text3d(locs[l,0],locs[l,1],locs[l,2], 'e'+ str(l+1), 10,'k')

        mne.viz.set_3d_view(figure=renderer.figure, distance=800,
                            focalpoint=(0., 30., 30.), elevation=105, azimuth=180)
        renderer.show()

        
    except:
        print("no electrodes recorded for participant")

   
    