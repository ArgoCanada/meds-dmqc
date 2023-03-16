
import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path

import bgcArgoDMQC as bgc

workshop_floats = [
    5906244, 5905519, 6902969, 6903874, 6903875, 6903876, 6903877,
    6903878, 6903549, 4903499, 4903500, 4903625, 6900889, 6900890,
    6902870, 6902807,
]

# make this true if it is the first time running it or haven't ran
# this script in a long time (i.e. there are likely additional profiles
# for active floats)
download = False
plot = False
if download:
    bgc.io.get_argo(workshop_floats, local_path=bgc.ARGO_PATH)

fig_path = Path('figures')
fig_path.mkdir(exist_ok=True)

sys.stdout.write('| WMO Number\t| Mean Gain |\n')
sys.stdout.write('| ------------- | --------- |\n')
for wmo in sorted(workshop_floats):
    flt = bgc.sprof(wmo)
    flt.clean()
    gains = flt.calc_gains(ref='WOA', verbose=False)
    sys.stdout.write(f'| {wmo}\t| {flt.gain:.3f}     |\n')


    if plot:
        g = flt.plot('gain', ref='WOA')
        g.axes[0].set_title(f'WMO: {wmo}', loc='left', fontweight='bold')
        g.axes[0].plot(flt.df.SDN.loc[flt.df.PRES < 50], flt.df.O2Sat.loc[flt.df.PRES < 50], 'o', zorder=0, alpha=0.1)
        g.fig.savefig(fig_path / f'{wmo}_gain.png', bbox_inches='tight', dpi=250)

        flt.reset()
        flt.rm_fillvalue()
        g = flt.plot('qcprofiles', varlist=['DOXY', 'DOXY_ADJUSTED', 'TEMP', 'PSAL'])
        g.fig.savefig(fig_path / f'{wmo}_qcprofiles.png', bbox_inches='tight', dpi=250)

        flt.clean()
        g = flt.plot('profiles', varlist=['DOXY', 'DOXY_ADJUSTED', 'TEMP', 'PSAL'])
        g.fig.savefig(fig_path / f'{wmo}_profiles.png', bbox_inches='tight', dpi=250)
