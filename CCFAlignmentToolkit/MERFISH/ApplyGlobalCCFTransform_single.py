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
import shutil
import os
import numpy as np

#Edit these parameters    
#---
inputDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/InvTransformInput'
baseDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNN_mouse3/iter0/'
baseName='mouse3'
#interpType='linear'
interpType='nearestNeighbor' #uncomment this line for label images
#---

#Sets up folders
mFishOrigStack=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/merfish_right_hemisphere.nii.gz'
mFishOrigStackIm=ants.image_read(mFishOrigStack)
outDir=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrigMatched'
os.makedirs(outDir, exist_ok=True)

#Run on each image in inputDir
#input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/ccf_right_hemisphere.nii.gz'
input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/reference_ccf_landmark_v2.nii.gz'
#input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/average_template_10.nii.gz'
#input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/annotation_10.nii.gz'
outname=Path(Path(input).stem).stem
inputImCCF=ants.image_read(input)
        
#Apply the global affine first from CCF to intermediate space
Tlist=[f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNinv_mouse3_v2/iter0/mouse3_v2_CCFGlobAffineMtx.mat']
warpedInputCCF = ants.apply_transforms(moving=inputImCCF,
                                             fixed=mFishOrigStackIm,
                                             transformlist=Tlist,
                                             interpolator=interpType,
                                             whichtoinvert=[False],
                                             verbose=True
                                            )
outReg = warpedInputCCF.copy()
#ants.image_write(outReg, f'{outDir}/CCFBroadLabels_AppliedGlobal.nii.gz')
ants.image_write(outReg, f'{outDir}/mouse3_v2_CCFLandmarksGlobWarpedNN_v2.nii.gz')
