#%%
import pytest
from utils import locate_edges
from pathlib import Path
trigger_channel = 'MISC005'
MEG_DATA_PATH = Path('/home/co/data/meg_distraction/240606')

def test_trigger():
    assert 1 == 1


def test_length():
    assert 1 == 1


#%%%
import mne
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
%matplotlib qt
matplotlib.use('Qt5Agg')

file_path_meg = MEG_DATA_PATH / "run1_raw.fif"

raw = mne.io.read_raw_fif(file_path_meg, preload=True, allow_maxshield=True)

picks = mne.pick_channels(raw.info['ch_names'], include=[trigger_channel])
#print(raw.info['ch_names'])
misc_data, times = raw[picks,:]

triggers = misc_data.T

#%%
# Define threshold and convert to int
# Do this but that works: for i in range(0.1, 1, 0.1):

for i in range(1, 10):
    triggers_bin = 1 * (triggers > i*0.1) 

    x, _ = locate_edges(triggers_bin)
    x = x / 1000 # in seconds
    y = np.ones(len(x)) 
    print(y.shape)

#%%
#print(locate_edges(triggers_bin))
triggers_bin = 1 * (triggers > 0.3) 

x, _ = locate_edges(triggers_bin)
x = x / 1000 # in seconds
y = np.ones(len(x)) 

print(y.shape)
#print(np.diff(x))
#print(len(x))


# plt.figure(figsize=(10,4))
# plt.plot(times,misc_data.T)
# plt.plot(x,y , 'o')
# plt.show()


#%%
# Open the metadata file to get the triggers onsets
metadata_file = MEG_DATA_PATH / "run1_old.tsv"
df = pd.read_csv(metadata_file, sep='\t')
print(df.head())

first_samp = raw.first_samp
sfreq = raw.info['sfreq']
triggers_onsets = df['onset'].values

print(triggers_onsets)
# %%

events = mne.find_events(raw)
first_trigger_time = events[1][0] / sfreq
# %%
shift = x[0] - triggers_onsets[0]
triggers_onsets = triggers_onsets + shift
plt.figure(figsize=(10,4))
plt.plot(x,y , 'o')
plt.plot(triggers_onsets, y, 'o')
plt.show()

# %%
triggers_onsets
# %%
y
# %%
