##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#
#Alternatively you can try a pre-comipled binary available for MacOS/Linux:
#
#   #pip install antspyx
#
#This is an example script for running various functions for fMOST image registration to the CCF
#Uncomment the sections below as needed.

import ants
from glob import glob
from pathlib import Path
import os
from CCFAlignmentToolkit.RegisterfMOSTtoCCF import RegisterfMOSTtoCCF
from CCFAlignmentToolkit.PreProcessfMOST import PreProcessfMOST
from CCFAlignmentToolkit.ApplyTransformTofMOST import  ApplyTransformTofMOST
from CCFAlignmentToolkit.ApplyTransformToSWC import ApplyTransformToSWC

#Input directories
InputBaseDir="/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data"
InputImgDir=f'{InputBaseDir}/202112201148_downsampled_volumes'
OrientDir=f'{InputBaseDir}/202112201620_orientation_templates'
SWCDir=f'{InputBaseDir}/HUST_REGISTRATION_AllCells_OriginalSent'
fMOSTtoCCFAtlasDir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/AtlasV6"

InputImgDir='/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Test'
#SWCDir='/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Test'

#Output Save Directories
OutputBaseDir="/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/OutputFull_5_25_2022"
RegOutDir = f'{OutputBaseDir}/RegOut'
TransformOutDir = f'{OutputBaseDir}/TransformOut'

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
    fMOSTFile_Preprocessed=PreProcessfMOST(fMOSTFile,RegOutDir)
    #RegisterfMOSTtoCCF(fMOSTFile,fMOSTtoCCFAtlasDir,RegOutDir,0)
    
    #Use this to apply tranforms to an image
    #ApplyTransformTofMOST(fMOSTFile, RegOutDir, fMOSTtoCCFAtlasDir, TransformOutDir) 
    
    #Search for SWC files
    #SWCAllFiles = glob(f'{SWCDir}/{imgID}*.swc')
    #print(SWCAllFiles)
    
    #Apply Transforms to the SWC files
    #for SWCFile in SWCAllFiles:
    #SWCFile=SWCAllFiles[0]
    #    ApplyTransformToSWC(SWCFile, fMOSTFile,OrientImgFiles[0], RegOutDir, fMOSTtoCCFAtlasDir, TransformOutDir)



