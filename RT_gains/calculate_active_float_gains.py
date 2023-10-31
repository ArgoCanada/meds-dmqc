#!/usr/bin/python

import numpy as np
import pandas as pd

import bgcArgoDMQC as bgc
import argopy
argopy.set_options(mode='expert')

# get list of active floats
ix = argopy.ArgoIndex(index_file='argo_bio-profile_index.txt').load().to_dataframe()
now = pd.Timestamp('now')
ix = ix.loc[(ix.institution_code == 'ME') & (ix.date > now - pd.Timedelta(weeks=4))]

# parse wmo numbers
ix['wmo'] = [int(s.split('/')[1]) for s in ix.file]

# read list of existing gains
rt_gains = pd.read_csv('rt_gains.csv')

no_sprof_file = [
    4902576, 4902577, 4902578, 4902579, 4902580, 4902582, 4902583,
    4902584, 4902585, 4902586, 4902587, 4902588, 4902589, 4902650,
    4902652, 4902660, 4902662, 4902663
]

with open('rt_gains.csv', 'a') as rt:
    # calculate gain for each any float that does not have one already
    for wmo in ix.wmo.unique():
        if wmo not in rt_gains.wmo.values and wmo not in no_sprof_file:
            # download data
            bgc.io.get_argo(wmo, local_path=bgc.io.Path.ARGO_PATH)
            # calculate gains
            try:
                flt = bgc.sprof(wmo)
                woa_gains = flt.calc_gains(ref='WOA')
                # last cycle
                max_cycle = flt.df.CYCLE.max()
                # write to to file
                rt.write(f'\n{wmo},{np.nanmean(woa_gains)},{now.strftime("%Y-%m-%d")},{max_cycle}')
            except FileNotFoundError:
                print(f'\n!!!!!!!!!!!! {wmo} !!!!!!!!!!!!\n')