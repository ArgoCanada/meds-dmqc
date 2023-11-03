
import ftplib
import pandas as pd


ftp = ftplib.FTP('ftp.ifremer.fr')
ftp.login()
ftp.cwd('/ifremer/argo/')
ix_fn = 'argo_bio-profile_index.txt.gz'
lf = open(ix_fn, 'wb')
ftp.retrbinary('RETR ' + ix_fn, lf.write)
lf.close()

ix = pd.read_csv(ix_fn, compression='gzip', header=8)
ix = ix.loc[ix['institution'] == 'ME']
all_bgc = ix.shape[0]
dm = ix.loc[[f.split('/')[-1][:2] == 'BD' for f in ix.file]]
dmqc_bgc = dm.shape[0]
a_mode_doxy = 0
mtime_only = 0
for param, mode in zip(ix.parameters, ix.parameter_data_mode):
    if 'DOXY' not in param:
        mtime_only += 1
    else:
        doxy_idx = param.split(' ').index('DOXY')
        if mode[doxy_idx] == 'A':
            a_mode_doxy += 1

eligible_bgc = all_bgc - mtime_only

with open('bgc_dmqc_tracker.csv', 'a') as f:
    today = pd.Timestamp('now').strftime('%Y-%m-%d')
    f.write(f'\n{today},{all_bgc},{dmqc_bgc},{100*dmqc_bgc/eligible_bgc},{a_mode_doxy},{100*a_mode_doxy/eligible_bgc},{eligible_bgc}')
