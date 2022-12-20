
import pandas as pd
import argopandas as argo

ix = argo.bio_prof
ix = ix.loc[ix['institution'] == 'ME']
all_bgc = ix.shape[0]
dm = ix.subset_data_mode('D')
dmqc_bgc = dm.shape[0]

with open('bgc_dmqc_tracker.csv', 'a') as f:
    today = pd.Timestamp('now').strftime('%Y-%m-%d')
    f.write(f'\n{today},{all_bgc},{dmqc_bgc},{100*dmqc_bgc/all_bgc}')
