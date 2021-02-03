#!/usr/bin/python

from pathlib import Path
from netCDF4 import Dataset

import bgcArgoDMQC as bgc

# This script will be used to DMQC a given float, as of the current date (feb
# 3, 2021), things are largely in a trial phase. This sort of "trial by fire"
# use of the package will likely lead to development in ArgoCanada/bgcArgoDMQC,
# which is exactly the idea. I will make an effort to do all DMQC in this file
# so that there is a clear diary of development on the github page. 

# Good luck me