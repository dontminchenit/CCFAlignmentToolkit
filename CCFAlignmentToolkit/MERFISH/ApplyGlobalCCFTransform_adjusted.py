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
mFishOrigStack=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/Mouse3/merfish_right_hemisphere_v2.nii.gz'
mFishOrigStackIm=ants.image_read(mFishOrigStack)
outDir=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Mouse3_AdjustGlobalTest'
os.makedirs(outDir, exist_ok=True)

#Run on each image in inputDir
#input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/ccf_right_hemisphere.nii.gz'
input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/reference_ccf_landmark_v2.nii.gz'
#input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/average_template_10.nii.gz'
#input='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/annotation_10.nii.gz'
outname='mouse3_v2'
inputImCCF=ants.image_read(input)

#Apply the global affine first from CCF to intermediate space
Tlist=[f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNinv_mouse3_v2/iter0/mouse3_v2_CCFGlobAffineMtx.mat']
Tlist_Adjust = '/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Mouse3_AdjustGlobalTest/CCFtoMouse3AffineAdjusted_LR5_AP5.mat'


def createNew(Tlist,inputImCCF,mFishOrigStackIm,interpType,saveLoc,LRval1,APval2):
    
    testT=ants.read_transform(Tlist[0])
    param = testT.parameters
    param[3]=param[3]+LRval1
    param[5]=param[5]+APval2
    testT.set_parameters(param)
    print(testT.parameters)
    ants.write_transform(testT,saveLoc)
    Tlist2 = [f'{saveLoc}']
    im = ants.apply_transforms(moving=inputImCCF,
                                                fixed=mFishOrigStackIm,
                                                transformlist=Tlist2,
                                                interpolator=interpType,
                                                whichtoinvert=[False],
                                                verbose=True
                                                )
    return im


imList=[]
sweep=np.linspace(-.25,.25,11)

#old code for sweeping
#for f in np.linspace(-.25,.25,11):
#    print(f)
#    im = createNew(Tlist,inputImCCF,mFishOrigStackIm,interpType,saveLoc,f,sweep[5])
#    im = createNew(Tlist,inputImCCF,mFishOrigStackIm,interpType,saveLoc,sweep[4],f)
#    imList.append(im)

#imgTar=ants.make_image(( *mFishOrigStackIm.shape, 2 ))
#imgTar.pixeltype=mFishOrigStackIm.pixeltype
#outReg = ants.list_to_ndimage(imgTar,imList)
#newDir = np.eye(4)
#newDir[0:3,0:3]=mFishOrigStackIm.direction
#outReg.set_direction(newDir)
#outReg.set_origin(mFishOrigStackIm.origin+(0,))
#outReg.set_spacing(mFishOrigStackIm.spacing+(1,))
#ants.image_write(outReg, f'{outDir}/mouse3_v2_CCFLandmarksGlobWarpedNN_LRc5_APsweep.nii.gz')
#ants.image_write(outReg, f'{outDir}/mouse3_v2_CCFLandmarksGlobWarpedNN_LRsweep_AP6.nii.gz')

im = createNew(Tlist,inputImCCF,mFishOrigStackIm,interpType,Tlist_Adjust,sweep[4],sweep[4])
ants.image_write(im, f'{outDir}/mouse3_v2_CCFLandmarksGlobWarpedNN_LR5_AP5.nii.gz')


mFishLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/Mouse3/Mouse3LabelsDilated.nii.gz'
CCFLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/reference_region_label.nii.gz'
CCFLandmarks='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/reference_ccf_landmark_v2.nii.gz'
CCFFullLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/annotation_10.nii.gz'
CCFAtlas='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/average_template_10.nii.gz'
CCFrHemi='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrig/ccf_right_hemisphere.nii.gz'

mFishLabelsIm = ants.image_read(mFishLabels)
CCFLabelsIm = ants.image_read(CCFLabels)
CCFLandmarksIm = ants.image_read(CCFLandmarks)
CCFFullLabelsIm = ants.image_read(CCFFullLabels)
CCFAtlasIm = ants.image_read(CCFAtlas)
CCFrHemiIm = ants.image_read(CCFrHemi)

Tlist=[f'{Tlist_Adjust}']

CCFLabelsWarped = ants.apply_transforms(moving=CCFLabelsIm,
                                        fixed=mFishLabelsIm,
                                        transformlist=Tlist,
                                        interpolator='nearestNeighbor',
                                        whichtoinvert=[False],
                                        verbose=True   
                                    )
ants.image_write(CCFLabelsWarped, f'{outDir}/{outname}_CCFGlobWarpedNN.nii.gz')

CCFFullLabelsWarped = ants.apply_transforms(moving=CCFFullLabelsIm,
                                        fixed=mFishLabelsIm,
                                        transformlist=Tlist,
                                        interpolator='nearestNeighbor',
                                        whichtoinvert=[False],
                                        verbose=True   
                                    )
ants.image_write(CCFFullLabelsWarped, f'{outDir}/{outname}_CCFFullGlobWarpedNN.nii.gz')

CCFLandmarksWarped = ants.apply_transforms(moving=CCFLandmarksIm,
                                        fixed=mFishLabelsIm,
                                        transformlist=Tlist,
                                        interpolator='nearestNeighbor',
                                        whichtoinvert=[False],
                                        verbose=True   
                                    )
ants.image_write(CCFLandmarksWarped, f'{outDir}/{outname}_CCFLandmarksGlobWarpedNN_v2.nii.gz')


CCFAtlasWarped = ants.apply_transforms(moving=CCFAtlasIm,
                                        fixed=mFishLabelsIm,
                                        transformlist=Tlist,
                                        interpolator='linear',
                                        whichtoinvert=[False],
                                        verbose=True   
                                    )
ants.image_write(CCFAtlasWarped, f'{outDir}/{outname}_CCFAtlasGlobWarped.nii.gz')


CCFrHemiWarped = ants.apply_transforms(moving=CCFrHemiIm,
                                        fixed=mFishLabelsIm,
                                        transformlist=Tlist,
                                        interpolator='nearestNeighbor',
                                        whichtoinvert=[False],
                                        verbose=True   
                                    )
ants.image_write(CCFrHemiWarped, f'{outDir}/{outname}_CCFRHemiGlobWarped.nii.gz')