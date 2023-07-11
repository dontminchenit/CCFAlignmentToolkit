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
baseDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNinv_mouse1/iter0/'
baseName='mouse1'
interpType='linear'
#interpType='nearestNeighbor' #uncomment this line for label images
#---

#Sets up folders
inputFilesCCF=glob(f'{inputDir}/*.nii.gz')
mFishOrigStack=f'{baseDir}input_mFish.nii.gz'
mFishOrigStackIm=ants.image_read(mFishOrigStack)
slcDir=f'{baseDir}slcTrans/'
outDir=f'{inputDir}/invwarpedImages/'
os.makedirs(outDir, exist_ok=True)

#Run on each image in inputDir
for input in inputFilesCCF:
        outname=Path(Path(input).stem).stem
        inputImCCF=ants.image_read(input)
        Nslc=mFishOrigStackIm.view().shape[2]
        
        #Apply the global affine first from CCF to intermediate space
        Tlist=[f'{baseDir}/{baseName}_CCFGlobAffineMtx.mat']
        warpedInputCCF = ants.apply_transforms(moving=inputImCCF,
                                             fixed=mFishOrigStackIm,
                                             transformlist=Tlist,
                                             interpolator=interpType,
                                             whichtoinvert=[False],
                                             verbose=True
                                            )

        outReg = warpedInputCCF.copy()
        #apply inv transforms to each section
        for i in range(Nslc):
            mFish_slc=ants.from_numpy(mFishOrigStackIm.view()[:,:,i])
            CCF_slc=ants.from_numpy(warpedInputCCF.view()[:,:,i])

            #Apply transforms
            Tlist=[f'{slcDir}{baseName}_fwdAffineMtx_slc{i}.mat', f'{slcDir}{baseName}_invDef_slc{i}.nii.gz']
            warped = ants.apply_transforms(moving=CCF_slc,
                                             fixed=mFish_slc,
                                             transformlist=Tlist,
                                             interpolator=interpType,
                                             whichtoinvert=[True, False],
                                             verbose=True   
                                             )
            outReg.view()[:,:,i]=warped.view()

        ants.image_write(outReg, f'{outDir}{outname}_AppliedWarpAllSlc.nii.gz')
