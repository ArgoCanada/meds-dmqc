#!/usr/bin/python

from pathlib import Path
from netCDF4 import Dataset

from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt

import bgcArgoDMQC as bgc

# This script will be used to DMQC a given float, as of the current date (feb
# 3, 2021), things are largely in a trial phase. This sort of "trial by fire"
# use of the package will likely lead to development in ArgoCanada/bgcArgoDMQC,
# which is exactly the idea. I will make an effort to do all DMQC in this file
# so that there is a clear diary of development on the github page. 

wmo_id = 4900523

# check if path where figures will be saved exists, make it if not
figpath = Path('../figures/{}'.format(wmo_id))
if not figpath.exists():
    figpath.mkdir()

syn  = bgc.sprof(wmo_id)

# calculate gains
woa_gains = syn.calc_gains(ref='WOA')
# air_gains = syn.calc_gains(ref='NCEP')

# make some plots
g_prof = syn.plot('qcprofiles', varlist=['PSAL_ADJUSTED', 'TEMP_ADJUSTED', 'DOXY_ADJUSTED'])
syn.clean()
g_prof2 = syn.plot('qcprofiles', varlist=['PSAL_ADJUSTED', 'TEMP_ADJUSTED', 'DOXY_ADJUSTED'])

figsize = (g_prof.fig.get_figwidth(), g_prof.fig.get_figheight())
g_prof.fig.savefig(Path('../figures/{}/qcprofiles.png'.format(wmo_id)), dpi=250, bbox_inches='tight')
g_prof2.fig.savefig(Path('../figures/{}/qcprofiles_cleaned.png'.format(wmo_id)), dpi=250, bbox_inches='tight')

g_gain = syn.plot('gain', ref='WOA')

g_gain.fig.savefig(Path('../figures/{}/gainplot.png'.format(wmo_id)), dpi=250, bbox_inches='tight')

DOXY_ADJUSTED = syn.DOXY * np.nanmean(woa_gains)
# add to float dict
syn.__floatdict__['DOXY_ADJUSTED_CALCULATED'] = DOXY_ADJUSTED
syn.assign(syn.__floatdict__)
syn.to_dataframe()

fig, ax = plt.subplots()
syn.plot('profiles', varlist=['DOXY'], axes=ax, color=plt.cm.GnBu_r(0.1), label=None)
syn.plot('profiles', varlist=['DOXY_ADJUSTED'], axes=ax, color=plt.cm.GnBu_r(0.35), label=None)
syn.plot('profiles', varlist=['DOXY_ADJUSTED_CALCULATED'], axes=ax, color=plt.cm.GnBu_r(0.6), label=None)

ax.plot([np.nan], [np.nan], color=plt.cm.GnBu_r(0.1), label='Raw')
ax.plot([np.nan], [np.nan], color=plt.cm.GnBu_r(0.35), label='Adjusted')
ax.plot([np.nan], [np.nan], color=plt.cm.GnBu_r(0.6), label='Python Package')

ax.legend(loc=3, fontsize=8)

fig.set_size_inches(figsize[0]/3, figsize[1])
fig.savefig(Path('../figures/{}/gainprofiles.png'.format(wmo_id)), dpi=250, bbox_inches='tight')

# load in comparison with SAGE output
sagefile = Path('/Users/gordonc/Documents/projects/external/ARGO_PROCESSING/MFILES/GUIS/SAGE_O2Argo/cgrdn_sprof/{}_sagedata.mat'.format(wmo_id))

if sagefile.exists():
        
    sagedata = loadmat(sagefile)

    sage_float = sagedata['SURF_SAT'][:,1]
    sage_woa = sagedata['WOAsurf'][0,:]
    py_woa = syn.__WOAref__
    py_float = syn.__WOAfloatref__[:,2]

    fig, axes = plt.subplots(1,2)
    axes[0].plot(sage_float, py_float, 'ko')
    axes[1].plot(sage_woa, py_woa, 'ko')

    xlim1 = axes[0].get_xlim()
    axes[0].plot(xlim1, xlim1, 'k-')
    axes[0].set_xlim(xlim1)
    axes[0].set_ylim(xlim1)
    axes[0].set_xlabel('SAGE Float % Sat')
    axes[0].set_ylabel('bgcArgoDMQC Float % Sat')

    xlim2 = axes[1].get_xlim()
    axes[1].plot(xlim2, xlim2, 'k-')
    axes[1].set_xlim(xlim2)
    axes[1].set_ylim(xlim2)
    axes[1].set_xlabel('SAGE WOA % Sat')
    axes[1].set_ylabel('bgcArgoDMQC WOA % Sat')

    fig.set_size_inches(figsize[0]*4/3, figsize[1])
    fig.savefig(Path('../figures/{}/sage_comparison.png'.format(wmo_id)), dpi=250, bbox_inches='tight')

    sage_factor = py_float / sage_float

    py_woa = syn.__WOAref__
    py_float = syn.__WOAfloatref__[:,2]

plt.show()
# plt.close('all')
