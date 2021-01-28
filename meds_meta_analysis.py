#!/usr/bin/python

from pathlib import Path
import numpy as np
import pandas as pd

from bgcArgoDMQC import get_index

# get the global and biogeochemical profile index
gbl = get_index('global')
bgc = get_index('bgc')
# only concerned with meds floats
meds_gbl = gbl[gbl.dac == 'meds']
meds_bgc = bgc[bgc.dac == 'meds']

# pre-allocate array for data mode of oxygen
doxy_mode = np.array(meds_bgc.shape[0]*[' '])
# loop through, find the location of oxygen in parameter, and extract the data mode
for i,ix in enumerate(meds_bgc.index):
    param_list = np.array(meds_bgc.loc[ix].parameters.split(' '))
    doxy_index = np.where(param_list == 'DOXY')[0][0]
    doxy_mode[i]  = meds_bgc.loc[ix].parameter_data_mode[doxy_index]
# add the data mode to the data frame
meds_bgc['doxy_mode'] = doxy_mode
# get the number of floats in each possible data mode
N_adjust = np.sum(meds_bgc.doxy_mode == 'A')
N_delay  = np.sum(meds_bgc.doxy_mode == 'D')
N_real   = np.sum(meds_bgc.doxy_mode == 'R')
# print them out
print(N_real, N_adjust, N_delay)

# now get the core file for each bio file, including if they are in different data modes
meds_bgc['core_file'] = np.array([f.replace('B', '') for f in meds_bgc.file])
meds_bgc['core_D_file'] = np.array([f.replace('BR', 'D') for f in meds_bgc.file])
meds_core_bgc = meds_gbl[meds_gbl.file.isin(meds_bgc.core_file) | meds_gbl.file.isin(meds_bgc.core_D_file)]

# pre-allocate array for data mode of core variables
core_mode = np.array(meds_core_bgc.shape[0]*[' '])
# loop through and get the data mode, just based on file name for core Argo
for i,ix in enumerate(meds_core_bgc.index):
    fn = meds_core_bgc.loc[ix].file
    core_mode[i] = fn.split('/')[-1][0]
# add to data frame
meds_core_bgc['core_mode'] = core_mode

# create a third data frame with the file names and oxygen data modes
# requires to match file names
df = pd.DataFrame()
df['bgc_file']  = meds_bgc.file
df['wmo']       = meds_bgc.wmo
df['cycle']     = meds_bgc.cycle

sorted_dm = np.array(doxy_mode.shape[0]*[' '])
for i, wmo, cyc in zip(range(doxy_mode.shape[0]), meds_core_bgc.wmo, meds_core_bgc.cycle):
    sorted_dm[i] = meds_core_bgc[np.logical_and(meds_core_bgc.wmo == wmo, meds_core_bgc.cycle == cyc)].core_mode.iloc[0]

df['core_mode'] = sorted_dm
df['doxy_mode'] = meds_bgc.doxy_mode
