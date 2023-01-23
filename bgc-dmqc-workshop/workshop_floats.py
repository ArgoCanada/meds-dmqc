
import warnings
warnings.filterwarnings('ignore')

import sys

import bgcArgoDMQC as bgc

workshop_floats = [
    5906244, 5905519, 6902969, 6903874, 6903875, 6903876, 6903877, \
    6903878, 6903549, 4903499, 4903500, 4903625, 6900889, 6900890,
]

# make this true if it is the first time running it or haven't ran
# this script in a long time (i.e. there are likely additional profiles
# for active floats)
download = True
if download:
    bgc.io.get_argo(workshop_floats, local_path=bgc.ARGO_PATH)

sys.stdout.write('| WMO Number\t| Mean Gain |\n')
sys.stdout.write('| ------------- | --------- |\n')
for wmo in workshop_floats:
    flt = bgc.sprof(wmo)
    gains = flt.calc_gains(ref='WOA', verbose=False)
    sys.stdout.write(f'| {wmo}\t| {flt.gain:.3f}     |\n')