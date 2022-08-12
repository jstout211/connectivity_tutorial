# connectivity_tutorial
This tutorial is primarily based on the Frites package

Additional information is on the tutorial wiki: <br>
  https://megcore.nih.gov/index.php/Meg_information_based_connectivity_coding_session
  
## Preprocessing Description
Dataset: NIMH hv protocol data in bids format.  Using the sternberg task (encode4 vs encode6) <br>
mne-bids-pipeline with default setting and 1-100Hz bandpass

## Code used for preprocessing - already performed - Zipped outputs below
Convert the epoched data to STCS sources <br> 
Convert STCS to epochs for reading into EPhysDataset format <br>
```
prep_sternberg_data.py  
```

# Dataset
The preprocessed data will be in the following folder: /vf/users/MEGmodules/modules/frites_dset.zip <br>
Download and unzip <br>
The `frites_root_dir` will be the path of the unzipped folder <b>

## Load data for processing
```
from load_data import load_dataset
ephys = load_dataset(frites_root_dir)  
```
