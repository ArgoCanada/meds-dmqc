#!/usr/bin/python

from pathlib import Path
from netCDF4 import Dataset

import numpy as np
import pandas as pd

import bgcArgoDMQC as bgc

# this script to serve as a template for performing D-mode file export. When
# export files for a given float, make a copy of this file and rename it 
# export_D-mode_files_[wmo].py. This way if you need to re-run the dmqc or
# export process, you can do so easily without having to alter a "living" 
# script.

exclude_dims = ['N_CALIB']
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
    'PROFILE_DOXY_QC'
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
    ('N_PROF')
]

wmo = 4900497
gain = 1.033
operater = 'Christopher Gordon'
affiliation = 'Fisheries and Oceans Canada'
orcid = '0000-0002-1756-422X'

float_path = Path('/Users/gordonc/Documents/data/Argo/meds/dac') / str(wmo) / 'profiles'
R_files = list(float_path.glob('BR*.nc'))

for fn in R_files:
    D_file = fn.as_posix().replace('BR', 'BD')
    R_nc = Dataset(fn)
    D_nc = bgc.io.copy_netcdf_except(
        fn, D_file, exclude_vars=exclude_vars,
        exclude_dims=exclude_dims
    )
    # create N_CALIB one greater than the previous one
    D_nc.createDimension('N_CALIB', size=R_nc.dimensions['N_CALIB'].size+1)
    # create the variables that you removed, but with the new N_CALIB
    for v,d in zip(exclude_vars, dims):
        D_nc.createVariable(
            v, R_nc[v].datatype, fill_value=R_nc[v]._FillValue,
            dimensions=d
        )
        D_nc[v].setncatts(R_nc[v].__dict__)
    
    # make the first N_CALIB dimension the same as the last one
    scientific_calib_comment = np.full(
        D_nc['SCIENTIFIC_CALIB_COMMENT'].shape,
        D_nc['SCIENTIFIC_CALIB_COMMENT']._FillValue,    
        dtype=D_nc['SCIENTIFIC_CALIB_COMMENT'].datatype
    )

    comment = 'Oxygen gain calculated following Johnson et al. 2015, doi:10.1175/JTECH-D-15-0101.1, using comparison between float and WOA data. Adjustment applied by {} ({}, orcid: {})'.format(operater, affiliation, orcid)
    N = len(comment)
    M = 256 - N
    comment = comment + M*' '
    comment = np.array(['{}'.format(let).encode('utf-8') for let in comment])
    scientific_calib_comment[0, 0, -1, :] = comment
    D_nc['SCIENTIFIC_CALIB_COMMENT'][:] = scientific_calib_comment
    
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
    scientific_calib_equation[0, 0, -1, :] = equation
    D_nc['SCIENTIFIC_CALIB_EQUATION'][:] = scientific_calib_equation

    scientific_calib_coefficient = np.full(
        D_nc['SCIENTIFIC_CALIB_COEFFICIENT'].shape,
        D_nc['SCIENTIFIC_CALIB_COEFFICIENT']._FillValue,    
        dtype=D_nc['SCIENTIFIC_CALIB_COEFFICIENT'].datatype
    )

    coeff = 'G = {}'.format(gain)
    N = len(coeff)
    M = 256 - N
    coeff = coeff + M*' '
    coeff = np.array(['{}'.format(let).encode('utf-8') for let in coeff])
    scientific_calib_coefficient[0, 0, 2, :] = R_nc['SCIENTIFIC_CALIB_COEFFICIENT'][:][0, 0, 2, :]
    scientific_calib_coefficient[0, 1, 2, :] = coeff
    D_nc['SCIENTIFIC_CALIB_COEFFICIENT'][:] = scientific_calib_coefficient

    doxy_adjusted = gain*D_nc['DOXY'][:].data
    D_nc['DOXY_ADJUSTED'][:] = doxy_adjusted
    doxy_adjusted_qc = D_nc['DOXY_QC'][:].data
    # note - for some older files there are 0 flags - meaning no QC was done at all
    doxy_adjusted_qc[doxy_adjusted_qc == b'0'] = b'3'
    D_nc['DOXY_QC'][:] = doxy_adjusted_qc
    doxy_adjusted_qc[doxy_adjusted_qc == b'3'] = b'2'
    D_nc['DOXY_ADJUSTED_QC'][:] = doxy_adjusted_qc
    D_nc['DOXY_ADJUSTED'][:][doxy_adjusted_qc == b'4'] = D_nc['DOXY_ADJUSTED']._FillValue

    molar_doxy_adjusted = gain*D_nc['MOLAR_DOXY'][:].data
    D_nc['MOLAR_DOXY_ADJUSTED'][:] = molar_doxy_adjusted
    molar_doxy_adjusted_qc = D_nc['MOLAR_DOXY_QC'][:].data
    molar_doxy_adjusted_qc[molar_doxy_adjusted_qc == b'3'] = b'2'
    D_nc['MOLAR_DOXY_ADJUSTED_QC'][:] = molar_doxy_adjusted_qc

    # D_nc['PARAMETER'][:] = R_nc['PARAMETER'][:]
    D_nc['DATA_MODE'][:] = np.array([b'D'])
    D_nc['PROFILE_DOXY_QC'][:] = np.array([b'D'])
    D_nc['PARAMETER_DATA_MODE'][:] = np.array([b'R', b'D', b'R', b'D'])

    try:
        sprof_nc = Dataset(fn.as_posix().replace('BR', 'SR'))
    except FileNotFoundError:
        sprof_nc = Dataset(fn.as_posix().replace('BR', 'SD'))

    S = sprof_nc['PSAL'][:]
    T = sprof_nc['TEMP'][:]
    P = D_nc['PRES'][:]

    D_nc['DOXY_ADJUSTED_ERROR'][:] = bgc.unit.pO2_to_doxy(4, S, T, P)
    D_nc['MOLAR_DOXY_ADJUSTED_ERROR'][:] = bgc.unit.umol_per_sw_to_mmol_per_L(D_nc['DOXY_ADJUSTED_ERROR'][:].data, S, T, P)

    R_nc.close()
    D_nc.close()