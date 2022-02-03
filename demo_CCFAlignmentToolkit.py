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

#Input directories
InputBaseDir="/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data"
InputImgDir=f'{InputBaseDir}/202112201148_downsampled_volumes'
OrientDir=f'{InputBaseDir}/202112201620_orientation_templates'
SWCDir=f'{InputBaseDir}/HUST_REGISTRATION_AllCells_OriginalSent'
fMOSTtoCCFAtlasDir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/AtlasV5"

#Output Save Directories
OutputBaseDir="/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Output_2_1_2022"
RegOutDir = f'{OutputBaseDir}/RegOut'
TransformOutDir = f'{OutputBaseDir}/TransformOut'

#SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/192343_5384-X4338-Y12696.swc'
#SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/182724_3887-X5901-Y10339.swc'
SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/swc/182724_1994-X7390-Y11953.swc'

#make output directories
os.makedirs(RegOutDir, exist_ok=True)
os.makedirs(TransformOutDir, exist_ok=True)


#loop through input images for RedChannel
inputFiles=glob(f'{InputImgDir}/*red*.nii.gz')
for fMOSTFile in inputFiles:
    print(fMOSTFile)
    
    #Find 6 digit ID for current image.
    outname = Path(Path(fMOSTFile).stem).stem
    imgID=outname[0:6]
    
    #Search for Orientation Header
    OrientImgFiles=glob(f'{OrientDir}/{imgID}*.nii.gz')
    print(OrientImgFiles[0])
   
    #Register Images 
    RegisterfMOSTtoCCF(fMOSTFile,fMOSTtoCCFAtlasDir,RegOutDir)
    
    #Use this to apply tranforms to an image
    #ApplyTransformTofMOST(fMOSTFile, RegOutDir, fMOSTtoCCFAtlasDir, TransformOutDir) 
    
    #Search for SWC files
    SWCAllFiles = glob(f'{SWCDir}/{imgID}*.swc')
    print(SWCAllFiles)
    
    #Apply Transforms to the SWC files
    for SWCFile in SWCAllFiles:
    #SWCFile=SWCAllFiles[0]
        ApplyTransformToSWC(SWCFile, fMOSTFile,OrientImgFiles[0], RegOutDir, fMOSTtoCCFAtlasDir, TransformOutDir)



