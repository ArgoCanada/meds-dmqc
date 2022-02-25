
import sys
from pathlib import Path
from netCDF4 import Dataset

import numpy as np
import pandas as pd

import bgcArgoDMQC as bgc

# float ID
wmo = 4900497
# date/time of DMQC
dmqc_date = '20220202154200'

# get gain from tracking spreadsheet
tracker = pd.read_csv(Path('../dmqc_tracker.csv'))
gain = tracker[tracker.wmo == wmo].gain.iloc[0]

# DMQC operator info
operater = 'Christopher Gordon'
affiliation = 'Fisheries and Oceans Canada'
orcid = '0000-0002-1756-422X'

# grab list of RT files
float_path = Path('/Users/GordonC/Documents/data/Argo/dac/meds') / str(wmo) / 'profiles'
R_files = list(float_path.glob('BR*.nc'))

# list of variables with N_CALIB as a dimension
calib_vars = [
    'SCIENTIFIC_CALIB_COMMENT', 
    'SCIENTIFIC_CALIB_EQUATION', 
    'SCIENTIFIC_CALIB_COEFFICIENT', 
    'SCIENTIFIC_CALIB_DATE',
]

for fn in R_files:
    # -------------------------------------------------------------------------
    # Section 1 - create D-mode file
    # -------------------------------------------------------------------------    

    # open the R file, we will use it later
    R_nc = Dataset(fn)
    # define path to file, make directory if it does not exist
    D_file = Path(fn.as_posix().replace('BR', 'BD').replace('dac/meds/', 'dac/meds/D/'))
    if not D_file.parent.exists():
        D_file.parent.mkdir(parents=True)
    sys.stdout.write(f'Working on D-mode file {D_file.as_posix()}...')

    # if existing N_CALIB is empty, just fill it in, if not empty, add 1 to N_CALIB dimension
    if bgc.io.check_for_empty_variables(fn, calib_vars):
        D_nc = bgc.io.copy_netcdf(fn, D_file)
    else:
        D_nc = bgc.io.iterate_dimension(fn, D_file, 'N_CALIB')
        # `PARAMETER` has `N_CALIB` dimension, so if we iterated in, fill in the last `N_CALIB`
        # with the same values as the first dimension
        D_nc['PARAMETER'][:][:,-1,:,:] = D_nc['PARAMETER'][:][:,0,:,:]
        last_calib = D_nc.dimensions['N_CALIB'].size-1

    # -------------------------------------------------------------------------
    # Section 2 - fill in SCIENTIFIC_CALIB information
    # -------------------------------------------------------------------------  

    # find index for DOXY along PARAMETER
    doxy_index = [bgc.io.read_ncstr(a) for a in D_nc['PARAMETER'][:].data[0,0,:,:]].index('DOXY')

    # fill in string info
    comment  = 'Oxygen gain calculated following Johnson et al. 2015, doi:10.1175/JTECH-D-15-0101.1, using comparison between float and WOA data. Adjustment applied by {} ({}, orcid: {})'.format(operater, affiliation, orcid)
    equation = 'DOXY_ADJUSTED = G*DOXY'
    coeff    = 'G = {}'.format(gain)

    # apply info to all profiles in file (not sure if this would ever not apply 
    # take caution when N_PROF > 1)
    for i in range(D_nc.dimensions['N_PROF'].size):
        D_nc['SCIENTIFIC_CALIB_COMMENT'][i,last_calib,doxy_index,:] = bgc.io.string_to_array(comment, D_nc.dimensions['STRING256'])
        D_nc['SCIENTIFIC_CALIB_EQUATION'][i,last_calib,doxy_index,:] = bgc.io.string_to_array(equation, D_nc.dimensions['STRING256'])
        D_nc['SCIENTIFIC_CALIB_COEFFICIENT'][i,last_calib,doxy_index,:] = bgc.io.string_to_array(coeff, D_nc.dimensions['STRING256'])

    # -------------------------------------------------------------------------
    # Section 3 - populate adjusted variables and flags
    # -------------------------------------------------------------------------  

    # populate DOXY_ADJUSTED
    doxy_adjusted = gain*D_nc['DOXY'][:].data
    doxy_adjusted_qc = D_nc['DOXY_QC'][:].data
    # note - for some older files there are 0 flags meaning no QC, changing to 2 based on visual QC
    doxy_adjusted_qc[doxy_adjusted_qc == b'0'] = b'2'
    D_nc['DOXY_QC'][:] = doxy_adjusted_qc
    doxy_adjusted_qc[doxy_adjusted_qc == b'3'] = b'2'
    # manual flag adjustment - visual inspection
    cycle = 83
    if R_nc['CYCLE_NUMBER'][:].compressed()[0] == cycle:
        ix = np.where(np.logical_and(R_nc['DOXY'][:].data > 250, R_nc['PRES'][:].data < 100))
        doxy_adjusted_qc[ix] = b'4'
        doxy_adjusted[ix] = D_nc['DOXY_ADJUSTED']._FillValue

    D_nc['DOXY_ADJUSTED'][:] = doxy_adjusted
    D_nc['DOXY_ADJUSTED_QC'][:] = doxy_adjusted_qc

    profile_doxy_qc = bgc.io.create_fillvalue_array(D_nc['PROFILE_DOXY_QC'])
    # populate PROFILE_DOXY_QC
    for i in range(D_nc.dimensions['N_PROF'].size):
        flags = bgc.io.read_qc(D_nc['DOXY_ADJUSTED_QC'][:].data[i,:])
        grade = bgc.profile_qc(pd.Series(flags)).encode('utf-8')
        profile_doxy_qc[i] = grade
    D_nc['PROFILE_DOXY_QC'][:] = profile_doxy_qc

    # get physical data for error calculation
    try:
        sprof_nc = Dataset(fn.as_posix().replace('BR', 'SR'))
    except FileNotFoundError:
        sprof_nc = Dataset(fn.as_posix().replace('BR', 'SD'))

    S = sprof_nc['PSAL'][:]
    T = sprof_nc['TEMP'][:]
    P = D_nc['PRES'][:]

    # populate adjusted error
    D_nc['DOXY_ADJUSTED_ERROR'][:] = bgc.unit.pO2_to_doxy(4, S, T, P)

    data_state_indicator = bgc.io.create_fillvalue_array(D_nc['DATA_STATE_INDICATOR'])
    for i in range(D_nc.dimensions['N_PROF'].size):
        data_state_indicator[i,:] = bgc.io.string_to_array('2C+', D_nc.dimensions['STRING4'])
    D_nc['DATA_STATE_INDICATOR'][:] = data_state_indicator

    history_dict = dict(
        HISTORY_INSTITUTION='BI',
        HISTORY_STEP='ARSQ',
        HISTORY_SOFTWARE='BGQC',
        HISTORY_SOFTWARE_RELEASE='v0.2',
        HISTORY_DATE=dmqc_date,
        HISTORY_ACTION='O2QC'
    )

    bgc.io.update_history(D_nc, history_dict)

    sys.stdout.write('done\n')