##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#

import ants
from glob import glob
from pathlib import Path
import os
from CCFAlignmentToolkit.RegisterfMOSTtoCCF import RegisterfMOSTtoCCF
from CCFAlignmentToolkit.ApplyTransformTofMOST import  ApplyTransformTofMOST
from CCFAlignmentToolkit.ApplyTransformToSWC import ApplyTransformToSWC

in_dir= "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest"
RegOutDir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/RegOut"
ApplyOutDir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/ApplyOut"
fMOSTtoCCFAtlasDir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/AtlasV5"
t=glob(f'{in_dir}/*.nii.gz')

SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/182724_3887-X5901-Y10339.swc'

#make output directories
os.makedirs(RegOutDir, exist_ok=True)
os.makedirs(ApplyOutDir, exist_ok=True)


#loop through input images
for fMOSTFile in t:
    print(fMOSTFile)
    RegisterfMOSTtoCCF(fMOSTFile,fMOSTtoCCFAtlasDir,RegOutDir)
    ApplyTransformTofMOST(fMOSTFile, RegOutDir, fMOSTtoCCFAtlasDir, ApplyOutDir) 
    ApplyTransformToSWC(SWCFile, fMOSTFile, RegOutDir, fMOSTtoCCFAtlasDir, ApplyOutDir)



