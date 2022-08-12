# connectivity_tutorial
This tutorial is primarily based on the Frites package

Additional information is on the tutorial wiki: <br>
  https://megcore.nih.gov/index.php/Meg_information_based_connectivity_coding_session
  
## Preprocessing
Dataset: NIMH hv protocol data in bids format.  Using the sternberg task (encode4 vs encode6) <br>
mne-bids-pipeline with default setting and 1-100Hz bandpass

## Convert to EPhysDataset format
Convert the epoched data to STCS sources <br> 
Convert STCS to epochs for reading into EPhysDataset format <br>
```
plot_dataset_mne.py  
```

# Dataset
Download the preprocessed data from the following folder: /vf/users/MEGmodules/modules/frites_dset.zip

## Load data for processing
```
from load_data import load_dataset
ephys = load_dataset(frites_root_dir)   #The sternberg data folder will be on biowulf
```
