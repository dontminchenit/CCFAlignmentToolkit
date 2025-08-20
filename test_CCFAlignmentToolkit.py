##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#
# Test script for running fMOST TO CCF registration

import ants
from glob import glob
from pathlib import Path
import os
from RegisterfMOSTtoCCF import RegisterfMOSTtoCCF

in_dir= "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/Inputs"
out_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/Outputs"
atlas_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/Atlas"
t=glob(f'{in_dir}/*.nii.gz')


for fMOSTFile in t:
    print(fMOSTFile)

    RegisterfMOSTtoCCF(fMOSTFile,atlas_dir,out_dir)


