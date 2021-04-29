#!/usr/bin/python

from pathlib import Path
from netCDF4 import Dataset

import numpy as np
import matplotlib.pyplot as plt

import bgcArgoDMQC as bgc

# This script will be used to DMQC a given float, as of the current date (feb
# 3, 2021), things are largely in a trial phase. This sort of "trial by fire"
# use of the package will likely lead to development in ArgoCanada/bgcArgoDMQC,
# which is exactly the idea. I will make an effort to do all DMQC in this file
# so that there is a clear diary of development on the github page. 

# Good luck me

# this is the first float to do BGC DMQC on
# deployed off NS shelf in March 2004
wmo_id = 4900497

# load BOTH the synthetic and individual profile files to redundantly check for
# differences in gain
syn  = bgc.sprof(wmo_id)
# prof = bgc.profiles(wmo_id)

# check the traj file - I doubt there is in-air data on a float that old but 
# who knows
# 
# there is a DOXY variable but not PPOX_DOXY - still, in-air gain will work
traj = Dataset(syn.__BRtraj__)
print(traj.variables.keys())

# calculate gains
woa_gains = syn.calc_gains(ref='WOA')

# make some plots
g_prof = syn.plot('qcprofiles', varlist=['PSAL', 'TEMP', 'DOXY'])
syn.clean()
g_prof2 = syn.plot('qcprofiles', varlist=['PSAL', 'TEMP', 'DOXY'])

g_gain = syn.plot('gain', ref='WOA')

DOXY_ADJUSTED = syn.DOXY * np.nanmean(woa_gains)
# add to float dict
syn.__floatdict__['DOXY_ADJUSTED_CALCULATED'] = DOXY_ADJUSTED
syn.assign(syn.__floatdict__)
syn.to_dataframe()

fig, ax = plt.subplots()
syn.plot('profiles', varlist=['DOXY'], axes=ax, color=plt.cm.Blues(0.25))
syn.plot('profiles', varlist=['DOXY_ADJUSTED'], axes=ax, color=plt.cm.Blues(0.5))
syn.plot('profiles', varlist=['DOXY_ADJUSTED_CALCULATED'], axes=ax, color=plt.cm.Blues(0.75))

plt.show()