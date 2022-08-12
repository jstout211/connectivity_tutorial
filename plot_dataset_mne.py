"""
Define an electrophysiological dataset using MNE-Python structures
==================================================================

This example illustrates how to define a dataset using MNE-Python Epochs.
"""
import numpy as np

from mne import EpochsArray, create_info
from frites.dataset import DatasetEphy
from frites import set_mpl_style
import mne_bids
from mne.minimum_norm import apply_inverse_epochs
from mne.minimum_norm import read_inverse_operator
import os

import matplotlib.pyplot as plt
from mne_bids import BIDSPath
import glob
import os 
import mne
import pandas as pd

set_mpl_style()

# =============================================================================
# Load MEG datasets from HV protocol
# =============================================================================

root = '/data/jstout/HVderivatives/mne-bids-pipeline'
subjects_dir =  '/data/jstout/HVderivatives/freesurfer/subjects'
frites_output_root = os.path.join(os.path.dirname(root), 'frites_dset')
if not os.path.exists(frites_output_root): os.mkdir(frites_output_root)

subjects = glob.glob(root+'/sub-*')
subjects = [os.path.basename(i).replace('sub-','') for i in subjects]




def preproc_frites(subject):
    fs_subject = 'sub-'+subject
    bids_path = BIDSPath(subject=subject, session='01', task='sternberg', run='01',
                         root=root, datatype='meg', suffix='meg')
    epochs_path = bids_path.copy().update(suffix='epo', extension='fif', processing='clean', run=None, check=False)
    epochs = mne.read_epochs(epochs_path.fpath)
    inv_bids_path = bids_path.copy().update(suffix='inv', extension='fif', run=None, check=False)
    inv = read_inverse_operator(inv_bids_path.fpath)
    fwd_bids_path = bids_path.copy().update(suffix='fwd', extension='fif', run=None,check=False)
    fwd = mne.read_forward_solution(fwd_bids_path.fpath)
    
    snr = 1.0
    lambda2 = 1.0 / snr ** 2
    
    labels_lh=mne.read_labels_from_annot(fs_subject, parc='aparc',
                                        subjects_dir=subjects_dir, hemi='lh') 
    labels_rh=mne.read_labels_from_annot(fs_subject, parc='aparc',
                                        subjects_dir=subjects_dir, hemi='rh') 
    labels=labels_lh + labels_rh 
    label_names = [i.name for i in labels]

    ## Encode4 processing
    stcs = apply_inverse_epochs(epochs['encode4'], inv, lambda2, 'MNE', verbose=True)
    [i.apply_baseline((-0.4, 0)) for i in stcs]  #HACK - not sure why this is needed
#    stcs = [abs(i) for i in stcs]
    
    label_ts = mne.extract_label_time_course(stcs, labels, fwd['src'], mode='pca_flip')
    
    #Convert list of numpy arrays to ndarray (Epoch/Label/Sample)
    label_stack = np.stack(label_ts)
    
    sf = epochs.info['sfreq']
    info = create_info(label_names, sf)
    epoch_encode4 = EpochsArray(label_stack, info, tmin=epochs.times[0],
                                verbose=False)
    epoch_encode4.events[:,2]*=4
    epoch_encode4.event_id={'4':4}
    
    ## Encode6 processing
    stcs = apply_inverse_epochs(epochs['encode6'], inv, lambda2, 'MNE', verbose=True)
    [i.apply_baseline((-0.4, 0)) for i in stcs]  #HACK - not sure why this is needed
#    stcs = [abs(i) for i in stcs]
    
    label_ts = mne.extract_label_time_course(stcs, labels, fwd['src'], mode='pca_flip')
    
    #Convert list of numpy arrays to ndarray (Epoch/Label/Sample)
    label_stack = np.stack(label_ts)
    
    sf = epochs.info['sfreq']
    info = create_info(label_names, sf)
    epoch_encode6 = EpochsArray(label_stack, info, tmin=epochs.times[0], 
                                verbose=False)   
    epoch_encode6.events[:,2]*=6
    epoch_encode6.event_id={'6':6}
    
    ## Combine and save
    epoch = mne.concatenate_epochs([epoch_encode4,epoch_encode6])
    
    epoch_frites_fname = os.path.join(frites_output_root, f'{subject}_epo.fif')
    epoch.save(epoch_frites_fname)

failed_subjs=[]
for subject in subjects:
    try:
        preproc_frites(subject)
    except:
        failed_subjs.append(subject)


# =============================================================================
# 
# =============================================================================
def load_mnedata():
    '''Return list of MNE source epochs'''
    x_mne = []
    epoch_files = glob.glob(frites_output_root+ '/*_epo.fif')
    sorted(epoch_files)
    for k in epoch_files:
        epoch = mne.read_epochs(k)
        # finally, replace it in the original list
        x_mne.append(epoch)
    return x_mne


def load_dataset():
    '''Load the MNE data, convert, and return EphysDataset'''
    x_mne = load_mnedata()
    labels_fname = os.path.join(frites_output_root, 'ROIs_DK.csv')
    #Save out the roi names if not done
    #pd.DataFrame(label_names, columns=['ROInames']).to_csv(labels_fname,index=False)
    rois = pd.read_csv(labels_fname).ROInames.tolist()
    
    times_fname = os.path.join(frites_output_root, 'Epoch_times.csv')
    #pd.DataFrame(epoch.times, columns=['Times']).to_csv(times_fname,index=False)
    times = pd.read_csv(times_fname).Times.tolist()
    
    dt = DatasetEphy(x_mne, 
                     y = [tmp_.events[:,2] for tmp_ in x_mne],
                     roi=[rois for i in range(len(x_mne))],
                     times=times)
    return dt



