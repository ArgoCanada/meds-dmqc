#!/usr/bin/python

from pathlib import Path
from netCDF4 import Dataset

from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt

import bgcArgoDMQC as bgc

# this script to serve as a template for performing DMQC. When DMQC-ing a
# float, make a copy of this file and rename it dmqc_[wmo].py. This way if
# you need to re-run the dmqc process, you can do so easily without having
# to alter a "living" script. 

# note - for now (Sept 19, 2021) you will need to have ran SAGE to get 
# some comparison data. As long as the file exists the wmo should fill in
# itself so will not require any additional user input. 

# float-specific code should go at the bottom and relevant plots should
# be re-made following those actions. NOTE: should make these higher level
# plots into functions for ease of use. Non-urgent can copy/paste for now.

# off southern coast of BC for its entire lifetime
wmo_id = 4900637

# check if path where figures will be saved exists, make it if not
figpath = Path('../figures/{}'.format(wmo_id))
if not figpath.exists():
    figpath.mkdir()

# load BOTH the synthetic and individual profile files to redundantly check for
# differences in gain
syn  = bgc.sprof(wmo_id)
# prof = bgc.profiles(wmo_id)

# make some plots
g_prof = syn.plot('qcprofiles', varlist=['PSAL_ADJUSTED', 'TEMP_ADJUSTED', 'DOXY_ADJUSTED'])
syn.clean()
g_prof2 = syn.plot('qcprofiles', varlist=['PSAL_ADJUSTED', 'TEMP_ADJUSTED', 'DOXY_ADJUSTED'])

figsize = (g_prof.fig.get_figwidth(), g_prof.fig.get_figheight())
g_prof.fig.savefig(Path('../figures/{}/qcprofiles.png'.format(wmo_id)), dpi=250, bbox_inches='tight')
g_prof2.fig.savefig(Path('../figures/{}/qcprofiles_cleaned.png'.format(wmo_id)), dpi=250, bbox_inches='tight')

# calculate gains - no BRtraj
woa_gains = syn.calc_gains(ref='WOA')
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

# add some extra plots
fig, axes = plt.subplots(3, 1, sharex=True)
vmin = dict(PSAL=30, TEMP=None, DOXY=120)
for ax, v in zip(axes, ['DOXY', 'TEMP', 'PSAL']):
    syn.plot('cscatter', varname=v, ax=ax, vmin=vmin[v])
    ax.set_ylim((150, 0))
fig.tight_layout()
fig.set_size_inches(4,6)

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

plt.show()
plt.close('all')