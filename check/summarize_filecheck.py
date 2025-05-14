
import sys
from pathlib import Path

import pandas as pd
from netCDF4 import Dataset
import bgcArgoDMQC as bgc

import xml.etree.ElementTree as ET

wmo = sys.argv[1]
files = list(Path(f'out/{wmo}/').glob('*.filecheck'))

N_FILES = len(files)
N_ACCEPTED = 0

for fn in files:
    tree = ET.parse(fn)
    N_ACCEPTED += int(tree.getroot()[1].text == 'FILE-ACCEPTED')
    
time = pd.Timestamp('now').strftime('%Y-%m-%d_%H%M')

parent = Path(f'summary/{wmo}')
parent.mkdir(exist_ok=True)
with open(parent / f'summary_{wmo}_{time}.txt', 'w') as f:
    f.write(f'\nNumber of profiles checked: {N_FILES}\n')
    f.write(f'Number of profiles accepted: {N_ACCEPTED}\n')

    if N_ACCEPTED == N_FILES:
        f.write('\nAll files accepted - ready to submit to GDAC\n')
        if (parent / 'files.txt').exists():
            (parent / 'files.txt').unlink()
    else:
        with open(parent / 'files.txt', 'w') as error_files:
            error_files.write('files')
            f.write(f'\n{N_FILES - N_ACCEPTED} files failed file check:\n\n')
            for fn in files:
                tree = ET.parse(fn)
                root = tree.getroot()
                if root[1].text != 'FILE-ACCEPTED':
                    error_files.write(f'\n{fn.name.replace(".filecheck", "")}')
                    f.write(f'{fn.name.replace(".filecheck", "")} errors:\n')
                    for e in root[4]:
                        f.write(f'\t-{e.text}\n')
    
    nc = Dataset(list(Path(f'/Users/GordonC/Documents/data/Argo/dac/meds/D/{wmo}/profiles/').glob(f'BD{wmo}*.nc'))[0])
    doxy_index = [bgc.io.read_ncstr(a) for a in nc['PARAMETER'][:].data[0,0,:,:]].index('DOXY')
    f.write('\nSCIENTIFIC_CALIB_COMMENT: ')
    f.write(f'{bgc.io.read_ncstr(nc["SCIENTIFIC_CALIB_COMMENT"][:][0,-1,doxy_index,:])}')
    f.write('\nSCIENTIFIC_CALIB_EQUATION: ')
    f.write(f'{bgc.io.read_ncstr(nc["SCIENTIFIC_CALIB_EQUATION"][:][0,-1,doxy_index,:])}')
    f.write('\nSCIENTIFIC_CALIB_COEFFICIENT: ')
    f.write(f'{bgc.io.read_ncstr(nc["SCIENTIFIC_CALIB_COEFFICIENT"][:][0,-1,doxy_index,:])}')

    