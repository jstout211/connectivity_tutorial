# connectivity_tutorial
This tutorial is primarily based on the Frites package

Additional information is on the tutorial wiki: 
  https://megcore.nih.gov/index.php/Meg_information_based_connectivity_coding_session
  
# Preprocessing
Dataset: NIMH hv protocol data in bids format.  Using the sternberg task (encode4 vs encode6)
mne-bids-pipeline with default setting and 1-100Hz bandpass

# Convert the data to STCS files and pack into EPhysDataset format
