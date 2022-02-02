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

#OrientImgFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Orig/mouse182724red_xy32z8.nii.gz'
#OrientImgFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Orig/192343_mm_SLA.nii.gz'
OrientImgFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Orig/182724_mm_SLA.nii.gz'
#SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/192343_5384-X4338-Y12696.swc'
#SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/182724_3887-X5901-Y10339.swc'
SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/182724_1994-X7390-Y11953.swc'

#make output directories
os.makedirs(RegOutDir, exist_ok=True)
os.makedirs(ApplyOutDir, exist_ok=True)


#loop through input images
for fMOSTFile in t:
    print(fMOSTFile)
    print(OrientImgFile)
    #RegisterfMOSTtoCCF(fMOSTFile,fMOSTtoCCFAtlasDir,RegOutDir)
    #ApplyTransformTofMOST(fMOSTFile, RegOutDir, fMOSTtoCCFAtlasDir, ApplyOutDir) 
    ApplyTransformToSWC(SWCFile, fMOSTFile,OrientImgFile, RegOutDir, fMOSTtoCCFAtlasDir, ApplyOutDir)



