# connectivity_tutorial
This tutorial is primarily based on the Frites package

Additional information is on the tutorial wiki: <br>
  https://megcore.nih.gov/index.php/Meg_information_based_connectivity_coding_session
  
## Preprocessing
Dataset: NIMH hv protocol data in bids format.  Using the sternberg task (encode4 vs encode6) <br>
mne-bids-pipeline with default setting and 1-100Hz bandpass

## Convert the epoched data to STCS sources <br> Convert STCS to epochs for reading into EPhysDataset format
plot_dataset_mne.py  
