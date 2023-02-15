# ECOG testing 02/14/23
Download the speech_basic.zip from:  https://searchworks.stanford.edu/view/zk881ps0522
```
from scipy.io import loadmat
matlab_dat = loadmat('....mat')
data = matlab_dat['data']
stim = matlab_dat['cues']
```

Install this package (plus frites and mne) 
```
pip install git+https://github.com/jstout211/connectivity_tutorial.git
```
OR
```
git clone https://github.com/jstout211/connectivity_tutorial.git
pip install -e ./connectivity_tutorial
```

###Convert the ECOG data to ephys (for frites processing)
```
from frites_connectivity_tutorial.load_data import load_dataset
dt = load_dataset(frites_root_dir)  
```




# connectivity_tutorial
This tutorial is primarily based on the Frites package

Additional information is on the tutorial wiki: <br>
  https://megcore.nih.gov/index.php/Meg_information_based_connectivity_coding_session
  
# Installation
```
pip install git+https://github.com/jstout211/connectivity_tutorial.git
```
  


# Dataset
The preprocessed data will be in the following folder on Biowulf: /vf/users/MEGmodules/modules/frites_dset.zip <br>
Download and unzip <br>
The `frites_root_dir` will be the path of the unzipped folder <b>

## Load data for processing
```
from frites_connectivity_tutorial.load_data import load_dataset
dt = load_dataset(frites_root_dir)  
```
## Expected active regions for sternberg
  based on 10.1016/j.schres.2008.06.013, the following regions should be active<br>
  `superiorparietal, superiorfrontal, frontalpole, medialorbitofrontal, parsopercularis, parstriangularis, rostralmiddlefrontal`
  
  
# Preprocessing Description
Dataset: NIMH hv protocol data in bids format.  Using the sternberg task (encode4 vs encode6) <br>
mne-bids-pipeline with default setting and 1-100Hz bandpass

## Code used for preprocessing - already performed - Zipped outputs listed above
Convert the epoched data to STCS sources <br> 
Convert STCS to epochs for reading into EPhysDataset format <br>
```
prep_sternberg_data.py  
```  

## mne-bids-pipeline config.py file
```
study_name = 'TESTSTudy'
bids_root = '/data/EnigmaMeg/BIDS/NIH_hvmeg_20220131'
l_freq = 1.0
h_freq = 100.
epochs_tmin = -0.6
epochs_tmax = 1.0
baseline = (-0.1, 0.0)
resample_sfreq = 300.0
ch_types = ['meg']
reject = dict(mag=4e-12)
session='01'
ses='01'
run='01'
task='sternberg'
conditions = ['encode4','encode6'] 
N_JOBS=12

subjects=["ON02747","ON02811","ON03748","ON05311","ON05530","ON06910","ON08392","ON08643","ON08792","ON10965","ON11394","ON12688","ON13545","ON13986","ON21976","ON22671","ON23483","ON25658","ON25939","ON26309","ON28693","ON33827","ON39099","ON40397","ON41090","ON42107","ON43016","ON43585","ON47254","ON48555","ON48925","ON49080","ON50015","ON52083","ON52662","ON54268","ON56044","ON56250","ON61373","ON62003","ON63734","ON66199","ON70467","ON72082","ON72409","ON73969","ON80038","ON81734","ON82386","ON84651","ON84896","ON85305","ON85616","ON86202","ON88614","ON89045","ON89474","ON89475","ON91906","ON93426","ON94856","ON95003","ON95422","ON95742","ON97504","ON99620"]

contrasts = [
    ('encode4', 'encode6')
]

on_error = 'continue' 
```

.
