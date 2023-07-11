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
#inputDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/registration_input/'
inputDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2/'
baseDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNinv_mouse3_v2/iter0/'
baseName='mouse3_v2'
#interpType='linear'
interpType='nearestNeighbor' #uncomment this line for label images
#---

#Sets up folders
inputFiles=glob(f'{inputDir}/*.nii.gz')
CCFLabels=f'{baseDir}{baseName}_CCFGlobWarpedNN.nii.gz'
CCFLabelsIm = ants.image_read(CCFLabels)
slcDir=f'{baseDir}slcTrans/'
outDir=f'{inputDir}/warpedImagesNN/'
os.makedirs(outDir, exist_ok=True)

#Run on each image in inputDir
for input in inputFiles:
        outname=Path(Path(input).stem).stem
        inputIm=ants.image_read(input)
        Nslc=inputIm.view().shape[2]
        outReg = inputIm.copy()
        #apply transforms to each section
        for i in range(Nslc):
            input_slc=ants.from_numpy(inputIm.view()[:,:,i])
            CCF_slc=ants.from_numpy(CCFLabelsIm.view()[:,:,i])

            #Apply transforms
            Tlist=[f'{slcDir}{baseName}_fwdDef_slc{i}.nii.gz', f'{slcDir}{baseName}_fwdAffineMtx_slc{i}.mat']
            warped = ants.apply_transforms(moving=input_slc,
                                             fixed=CCF_slc,
                                             transformlist=Tlist,
                                             interpolator=interpType,
                                             whichtoinvert=[False, False],
                                             verbose=True   
                                             )
            outReg.view()[:,:,i]=warped.view()

        ants.image_write(outReg, f'{outDir}{outname}_AppliedWarpAllSlc.nii.gz')
