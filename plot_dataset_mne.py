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
set_mpl_style()

# =============================================================================
# Load MEG datasets from HV protocol
# =============================================================================

root = '/data/jstout/HVderivatives/mne-bids-pipeline'
subjects_dir =  '/data/jstout/HVderivatives/freesurfer/subjects'
frites_output_root = os.path.join(os.path.dirname(root), 'frites_dset')
if not os.path.exists(frites_output_root): os.mkdir(frites_output_root)

from mne_bids import BIDSPath
import glob
import os 
import mne

subjects = glob.glob(root+'/sub-*')
subjects = [os.path.basename(i).replace('sub-','') for i in subjects]
subject = subjects[0]
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
stcs = apply_inverse_epochs(epochs, inv, lambda2, 'MNE', verbose=True)
stcs = [abs(i) for i in stcs]

labels_lh=mne.read_labels_from_annot(fs_subject, parc='aparc',
                                    subjects_dir=subjects_dir, hemi='lh') 
labels_rh=mne.read_labels_from_annot(fs_subject, parc='aparc',
                                    subjects_dir=subjects_dir, hemi='rh') 
labels=labels_lh + labels_rh 
label_names = [i.name for i in labels]

label_ts = mne.extract_label_time_course(stcs, labels, fwd['src'], mode='pca_flip')

#Convert list of numpy arrays to ndarray (Epoch/Label/Sample)
label_stack = np.stack(label_ts)

sf = epochs.info['sfreq']
info = create_info(label_names, sf)
epoch = EpochsArray(label_stack, info, tmin=epochs.times[0], verbose=False)






x_mne = []
for k in range(n_subjects):
    # create some informations
    info = create_info(ch[k].tolist(), sf)
    # create the Epoch of this subject
    epoch = EpochsArray(x[k], info, tmin=times[0], verbose=False)
    # finally, replace it in the original list
    x_mne.append(epoch)
print(x_mne[0])

###############################################################################
# Build the dataset
# -----------------
#
# Finally, we pass the data to the :class:`frites.dataset.DatasetEphy` class
# in order to create the dataset

dt = DatasetEphy(x_mne)
print(dt)

print('Time vector : ', dt.times)
print('ROI DataFrame\n: ', dt.df_rs)
