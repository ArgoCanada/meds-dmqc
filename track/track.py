
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

with open('bgc_dmqc_tracker.csv', 'a') as f:
    today = pd.Timestamp('now').strftime('%Y-%m-%d')
    f.write(f'\n{today},{all_bgc},{dmqc_bgc},{100*dmqc_bgc/all_bgc}')
