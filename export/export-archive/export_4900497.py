#!/usr/bin/python

import sys
from pathlib import Path
from netCDF4 import Dataset

import numpy as np
import pandas as pd

import bgcArgoDMQC as bgc

exclude_dims = ['N_CALIB', 'N_HISTORY']
exclude_vars = [
    'SCIENTIFIC_CALIB_COMMENT', 
    'SCIENTIFIC_CALIB_EQUATION', 
    'SCIENTIFIC_CALIB_COEFFICIENT', 
    'SCIENTIFIC_CALIB_DATE',
    'PARAMETER',
    'DOXY_ADJUSTED',
    'DATA_MODE',
    'PARAMETER_DATA_MODE',
    'DOXY_ADJUSTED_QC',
    'PROFILE_DOXY_QC',
    'HISTORY_INSTITUTION',
    'HISTORY_STEP',
    'HISTORY_SOFTWARE',
    'HISTORY_SOFTWARE_RELEASE',
    'HISTORY_REFERENCE',
    'HISTORY_DATE',
    'HISTORY_ACTION',
    'HISTORY_PARAMETER',
    'HISTORY_START_PRES',
    'HISTORY_STOP_PRES',
    'HISTORY_PREVIOUS_VALUE',
    'HISTORY_QCTEST',
    'DATA_STATE_INDICATOR',
]
dims = [
    ('N_PROF', 'N_CALIB', 'N_PARAM', 'STRING256'),
    ('N_PROF', 'N_CALIB', 'N_PARAM', 'STRING256'),
    ('N_PROF', 'N_CALIB', 'N_PARAM', 'STRING256'),
    ('N_PROF', 'N_CALIB', 'N_PARAM', 'DATE_TIME'),
    ('N_PROF', 'N_CALIB', 'N_PARAM', 'STRING64'),
    ('N_PROF', 'N_LEVELS'),
    ('N_PROF'),
    ('N_PROF', 'N_PARAM'),
    ('N_PROF', 'N_LEVELS'),
    ('N_PROF'),
    ('N_HISTORY', 'N_PROF', 'STRING4'),
    ('N_HISTORY', 'N_PROF', 'STRING4'),
    ('N_HISTORY', 'N_PROF', 'STRING4'),
    ('N_HISTORY', 'N_PROF', 'STRING4'),
    ('N_HISTORY', 'N_PROF', 'STRING64'),
    ('N_HISTORY', 'N_PROF', 'DATE_TIME'),
    ('N_HISTORY', 'N_PROF', 'STRING4'),
    ('N_HISTORY', 'N_PROF', 'STRING64'),
    ('N_HISTORY', 'N_PROF'),
    ('N_HISTORY', 'N_PROF'),
    ('N_HISTORY', 'N_PROF'),
    ('N_HISTORY', 'N_PROF', 'STRING16'),
    ('N_PROF', 'STRING4'),
]

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

# index for DOXY according to PARAMETER - should be automated not hard coded
doxy_ix = 1

# loop through files
for fn in R_files:
    # create DM file
    D_file = Path(fn.as_posix().replace('BR', 'BD').replace('dac/meds/', 'dac/meds/D/'))
    if not D_file.parent.exists():
        D_file.parent.mkdir(parents=True)
    sys.stdout.write(f'Working on D-mode file {D_file.as_posix()}...')
    # load RT data
    R_nc = Dataset(fn)
    # copys RT data except for those variables in exclude_vars or with
    # dimensions in exclude_dims
    D_nc = bgc.io.copy_netcdf_except(
        fn, D_file, exclude_vars=exclude_vars,
        exclude_dims=exclude_dims
    )
    # create N_CALIB one greater than the previous one
    D_nc.createDimension('N_CALIB', size=R_nc.dimensions['N_CALIB'].size+1)
    # create N_HISTORY one greater than the previous one
    D_nc.createDimension('N_HISTORY', size=R_nc.dimensions['N_HISTORY'].size+1)
    # create the variables that you removed, but with the new N_CALIB
    for v, d in zip(exclude_vars, dims):
        D_nc.createVariable(
            v, R_nc[v].datatype, 
            fill_value=R_nc[v]._FillValue,
            dimensions=d
        )
        D_nc[v].setncatts(R_nc[v].__dict__)
    
    # make the first N_CALIB dimension the same as the last one
    scientific_calib_comment = np.full(
        D_nc['SCIENTIFIC_CALIB_COMMENT'].shape,
        D_nc['SCIENTIFIC_CALIB_COMMENT']._FillValue,    
        dtype=D_nc['SCIENTIFIC_CALIB_COMMENT'].datatype
    )

    # add scientific calibration comment
    comment = 'Oxygen gain calculated following Johnson et al. 2015, doi:10.1175/JTECH-D-15-0101.1, using comparison between float and WOA data. Adjustment applied by {} ({}, orcid: {})'.format(operater, affiliation, orcid)
    N = len(comment)
    M = 256 - N
    comment = comment + M*' '
    comment = np.array(['{}'.format(let).encode('utf-8') for let in comment])
    for i in range(R_nc.dimensions['N_CALIB'].size):
        scientific_calib_comment[:, i, :, :] = R_nc['SCIENTIFIC_CALIB_COMMENT'][:][:, i, :, :]
    scientific_calib_comment[0, -1, doxy_ix, :] = comment
    D_nc['SCIENTIFIC_CALIB_COMMENT'][:] = scientific_calib_comment
    
    # add scientific calibration equation
    scientific_calib_equation = np.full(
        D_nc['SCIENTIFIC_CALIB_EQUATION'].shape,
        D_nc['SCIENTIFIC_CALIB_EQUATION']._FillValue,    
        dtype=D_nc['SCIENTIFIC_CALIB_EQUATION'].datatype
    )
    equation = 'DOXY_ADJUSTED = G*DOXY'
    N = len(equation)
    M = 256 - N
    equation = equation + M*' '
    equation = np.array(['{}'.format(let).encode('utf-8') for let in equation])
    for i in range(R_nc.dimensions['N_CALIB'].size):
        scientific_calib_equation[:, i, :, :] = R_nc['SCIENTIFIC_CALIB_EQUATION'][:][:, i, :, :]
    scientific_calib_equation[0, -1, doxy_ix, :] = equation
    D_nc['SCIENTIFIC_CALIB_EQUATION'][:] = scientific_calib_equation

    scientific_calib_coefficient = np.full(
        D_nc['SCIENTIFIC_CALIB_COEFFICIENT'].shape,
        D_nc['SCIENTIFIC_CALIB_COEFFICIENT']._FillValue,    
        dtype=D_nc['SCIENTIFIC_CALIB_COEFFICIENT'].datatype
    )

    # add gain coefficient
    coeff = 'G = {}'.format(gain)
    N = len(coeff)
    M = 256 - N
    coeff = coeff + M*' '
    coeff = np.array(['{}'.format(let).encode('utf-8') for let in coeff])
    for i in range(R_nc.dimensions['N_CALIB'].size):
        scientific_calib_coefficient[:, i, :, :] = R_nc['SCIENTIFIC_CALIB_COEFFICIENT'][:][:, i, :, :]
    scientific_calib_coefficient[0, -1, doxy_ix, :] = coeff
    D_nc['SCIENTIFIC_CALIB_COEFFICIENT'][:] = scientific_calib_coefficient

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
    
    profile_doxy_qc = np.full(
        D_nc['PROFILE_DOXY_QC'].shape,
        D_nc['PROFILE_DOXY_QC']._FillValue,    
        dtype=D_nc['PROFILE_DOXY_QC'].datatype
    )
    # populate PROFILE_DOXY_QC
    for i in range(D_nc.dimensions['N_PROF'].size):
        flags = bgc.util.read_qc(D_nc['DOXY_ADJUSTED_QC'][:].data[i,:])
        grade = bgc.profile_qc(pd.Series(flags)).encode('utf-8')
        profile_doxy_qc[i] = grade
    D_nc['PROFILE_DOXY_QC'][:] = profile_doxy_qc

    # don't worry about MOLAR_DOXY anymore
    # molar_doxy_adjusted = gain*D_nc['MOLAR_DOXY'][:].data
    # D_nc['MOLAR_DOXY_ADJUSTED'][:] = molar_doxy_adjusted
    # molar_doxy_adjusted_qc = D_nc['MOLAR_DOXY_QC'][:].data
    # molar_doxy_adjusted_qc[molar_doxy_adjusted_qc == b'3'] = b'2'
    # D_nc['MOLAR_DOXY_ADJUSTED_QC'][:] = molar_doxy_adjusted_qc

    parameter = np.full(
        D_nc['PARAMETER'].shape,
        D_nc['PARAMETER']._FillValue,    
        dtype=D_nc['PARAMETER'].datatype
    )

    for i in range(R_nc.dimensions['N_CALIB'].size):
        parameter[:,i,:,:] = R_nc['PARAMETER'][:][:,i,:,:]
    parameter[:,-1,:,:] = R_nc['PARAMETER'][:][:,-1,:,:]
    D_nc['PARAMETER'][:] = parameter
    # NOTE: this is manual right now, long term should not be
    D_nc['DATA_MODE'][:] = np.array([b'D'])
    D_nc['PROFILE_DOXY_QC'][:] = np.array([b'D'])
    D_nc['PARAMETER_DATA_MODE'][:] = np.array([b'R', b'D', b'R', b'R'])

    try:
        sprof_nc = Dataset(fn.as_posix().replace('BR', 'SR'))
    except FileNotFoundError:
        sprof_nc = Dataset(fn.as_posix().replace('BR', 'SD'))

    S = sprof_nc['PSAL'][:]
    T = sprof_nc['TEMP'][:]
    P = D_nc['PRES'][:]

    # populate adjusted error
    D_nc['DOXY_ADJUSTED_ERROR'][:] = bgc.unit.pO2_to_doxy(4, S, T, P)
    # D_nc['MOLAR_DOXY_ADJUSTED_ERROR'][:] = bgc.unit.umol_per_sw_to_mmol_per_L(D_nc['DOXY_ADJUSTED_ERROR'][:].data, S, T, P)

    # history variables
    
    # copy variable but leave last slot open
    history_institution = np.full(
        D_nc['HISTORY_INSTITUTION'].shape,
        D_nc['HISTORY_INSTITUTION']._FillValue,    
        dtype=D_nc['HISTORY_INSTITUTION'].datatype
    )
    institution = 'BI'
    M = D_nc.dimensions['STRING4'].size - len(institution)
    institution = institution + M*' '
    institution = np.array(['{}'.format(let).encode('utf-8') for let in institution])
    for i in range(R_nc.dimensions['N_HISTORY'].size):
        history_institution[i, :, :] = R_nc['HISTORY_INSTITUTION'][:][i, :, :]
    history_institution[-1, :, :] = institution
    D_nc['HISTORY_INSTITUTION'][:] = history_institution

    history_step = np.full(
        D_nc['HISTORY_STEP'].shape,
        D_nc['HISTORY_STEP']._FillValue,    
        dtype=D_nc['HISTORY_STEP'].datatype
    )
    step = 'ARSQ'
    M = D_nc.dimensions['STRING4'].size - len(step)
    step = step + M*' '
    step = np.array(['{}'.format(let).encode('utf-8') for let in step])
    for i in range(R_nc.dimensions['N_HISTORY'].size):
        history_step[i, :, :] = R_nc['HISTORY_STEP'][:][i, :, :]
    history_step[-1, :, :] = step
    D_nc['HISTORY_STEP'][:] = history_step

    history_software = np.full(
        D_nc['HISTORY_SOFTWARE'].shape,
        D_nc['HISTORY_SOFTWARE']._FillValue,    
        dtype=D_nc['HISTORY_SOFTWARE'].datatype
    )
    software = 'BGQC'
    M = D_nc.dimensions['STRING4'].size - len(software)
    software = software + M*' '
    software = np.array(['{}'.format(let).encode('utf-8') for let in software])
    for i in range(R_nc.dimensions['N_HISTORY'].size):
        history_software[i, :, :] = R_nc['HISTORY_SOFTWARE'][:][i, :, :]
    history_software[-1, :, :] = software
    D_nc['HISTORY_SOFTWARE'][:] = history_software

    history_software_release = np.full(
        D_nc['HISTORY_SOFTWARE_RELEASE'].shape,
        D_nc['HISTORY_SOFTWARE_RELEASE']._FillValue,    
        dtype=D_nc['HISTORY_SOFTWARE_RELEASE'].datatype
    )
    release = 'v0.2'
    M = D_nc.dimensions['STRING4'].size - len(release)
    release = release + M*' '
    release = np.array(['{}'.format(let).encode('utf-8') for let in release])
    for i in range(R_nc.dimensions['N_HISTORY'].size):
        history_software_release[i, :, :] = R_nc['HISTORY_SOFTWARE_RELEASE'][:][i, :, :]
    history_software_release[-1, :, :] = release
    D_nc['HISTORY_SOFTWARE_RELEASE'][:] = history_software_release

    history_date = np.full(
        D_nc['HISTORY_DATE'].shape,
        D_nc['HISTORY_DATE']._FillValue,    
        dtype=D_nc['HISTORY_DATE'].datatype
    )
    
    M = D_nc.dimensions['DATE_TIME'].size - len(dmqc_date)
    date = dmqc_date + M*' '
    date = np.array(['{}'.format(let).encode('utf-8') for let in date])
    for i in range(R_nc.dimensions['N_HISTORY'].size):
        history_date[i, :, :] = R_nc['HISTORY_DATE'][:][i, :, :]
    history_date[-1, :, :] = date
    D_nc['HISTORY_DATE'][:] = history_date

    history_action = np.full(
        D_nc['HISTORY_ACTION'].shape,
        D_nc['HISTORY_ACTION']._FillValue,    
        dtype=D_nc['HISTORY_ACTION'].datatype
    )
    action = 'O2QC'
    M = D_nc.dimensions['STRING4'].size - len(action)
    action = action + M*' '
    action = np.array(['{}'.format(let).encode('utf-8') for let in action])
    for i in range(R_nc.dimensions['N_HISTORY'].size):
        history_action[i, :, :] = R_nc['HISTORY_ACTION'][:][i, :, :]
    history_action[-1, :, :] = action
    D_nc['HISTORY_ACTION'][:] = history_action

    for v in ['HISTORY_REFERENCE', 'HISTORY_START_PRES', 'HISTORY_STOP_PRES', 'HISTORY_PREVIOUS_VALUE', 'HISTORY_QCTEST']:
        blank = np.full(
            D_nc[v].shape,
            D_nc[v]._FillValue,    
            dtype=D_nc[v].datatype
        )
        D_nc[v][:] = blank

    data_state_indicator = np.full(
        D_nc['DATA_STATE_INDICATOR'].shape,
        D_nc['DATA_STATE_INDICATOR']._FillValue,    
        dtype=D_nc['DATA_STATE_INDICATOR'].datatype
    )
    state = '2C+'
    M = D_nc.dimensions['STRING4'].size - len(state)
    state = state + M*' '
    state = np.array(['{}'.format(let).encode('utf-8') for let in state])
    data_state_indicator[0,:] = state
    D_nc['DATA_STATE_INDICATOR'][:] = data_state_indicator
    
    sys.stdout.write('done\n')

    R_nc.close()
    D_nc.close()