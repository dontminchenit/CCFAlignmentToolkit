##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#
# Step 1: Global registration of MERFISH brain into the CCF to match the correct global orientation of the brains.
#    Script: RegistermFishtoCCFGlobal.py
#    Inputs:
#        outname - name prefix attached to results
#        mFishLabels - Broad labels for tissue types in the MERFISH image
#        CCFLabels - Broad labels for tissue types in the Allen CCF
#        CCFLandmarks - Fine labels for key structures in the MERFISH image
#        CCFFullLabels - Fine labels for key structures in the Allen CCF
#        CCFAtlas - Allen CCF atlas image
#        outDirBase - Base directory where results will be saved
#    Outputs:
#        Generate the initial global transform. A file ending with "*_CCFGlobAffineMtx.mat" in the outDirBase

import ants
#from glob import glob
from pathlib import Path
import shutil
import os
import numpy as np
    

outname='mouse3_v2'

mFishLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/Mouse3LabelsDilated.nii.gz'
CCFLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/AllLabelsCCF_v2.nii.gz'
CCFLandmarks='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/reference_ccf_landmark.nii.gz'
CCFFullLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/annotation_10.nii.gz'
CCFAtlas='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/average_template_10.nii.gz'

mFishLabelsImOrig = ants.image_read(mFishLabels)
Nslc=mFishLabelsImOrig.view().shape[2]

print(Nslc)

mFishLabelsIm = ants.image_read(mFishLabels)
CCFLabelsIm = ants.image_read(CCFLabels)
CCFLandmarksIm = ants.image_read(CCFLandmarks)
CCFFullLabelsIm = ants.image_read(CCFFullLabels)
CCFAtlasIm = ants.image_read(CCFAtlas)
outDirBase=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNregapped2_{outname}/'

os.makedirs(outDirBase,exist_ok=True)
    

for iter in range(1):
        outDir=f'{outDirBase}/iter{iter}/'
        os.makedirs(outDir,exist_ok=True)
        ants.image_write(mFishLabelsIm, f'{outDir}/input_mFish.nii.gz')
        ants.image_write(CCFLabelsIm, f'{outDir}/input_CCF.nii.gz')
        registration = ants.registration(fixed=mFishLabelsIm, 
                                             moving=CCFLabelsIm,
                                             type_of_transform='Affine',
                                             verbose=True
                                             )

        #move warped image
        ants.image_write(registration['warpedmovout'], f'{outDir}/{outname}_CCFGlobWarped.nii.gz')
        resultToMerFish = registration['warpedmovout']    
            
        #saveTransforms
        shutil.move(registration['fwdtransforms'][0],f'{outDir}/{outname}_CCFGlobAffineMtx.mat')

        Tlist=[f'{outDir}/{outname}_CCFGlobAffineMtx.mat']

        warped1 = ants.apply_transforms(moving=CCFLabelsIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warped1, f'{outDir}/{outname}_CCFGlobWarpedNN.nii.gz')
        
        warped = ants.apply_transforms(moving=CCFFullLabelsIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warped, f'{outDir}/{outname}_CCFFullGlobWarpedNN.nii.gz')
        
        warped = ants.apply_transforms(moving=CCFLandmarksIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warped, f'{outDir}/{outname}_CCFLandmarksGlobWarpedNN.nii.gz')
        
        
        warped = ants.apply_transforms(moving=CCFAtlasIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='linear',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warped, f'{outDir}/{outname}_CCFAtlasGlobWarped.nii.gz')

        #warped=ants.image_read('/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelim/AllLabelsCCF_WarpedNN.nii.gz')

        outReg = mFishLabelsImOrig.copy()
        os.makedirs(f'{outDir}/slcTrans', exist_ok=True)
       
        if false:#Use this to turn off slice registration
        #for i in range(Nslc):
            mFish_slc=ants.from_numpy(mFishLabelsImOrig.view()[:,:,i])
            CCF_slc=ants.from_numpy(warped1.view()[:,:,i])

            #check if slc is empty
            slcsum=np.sum(mFish_slc.view())
            if slcsum == 0:
                mFish_slc=CCF_slc

            registration = ants.registration(fixed=CCF_slc,
                                             moving=mFish_slc, 
                                             type_of_transform='antsRegistrationSyNQuick[s]', #type_of_transform='Rigid',
                                             verbose=True
                                             )
                                             #type_of_transform='Rigid',
                                             #verbose=True
                                             #)
            Tlist=registration['fwdtransforms']
            warpedslc = ants.apply_transforms(moving=mFish_slc,
                                             fixed=CCF_slc,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False,False],
                                             verbose=True   
                                            )

            if slcsum != 0:
                #outSlc=registration['warpedmovout']
                #outReg.view()[:,:,i]=outSlc.view()
                outReg.view()[:,:,i]=warpedslc.view()
            shutil.move(registration['fwdtransforms'][1],f'{outDir}/slcTrans/{outname}_fwdAffineMtx_slc{i}.mat')
            shutil.move(registration['fwdtransforms'][0],f'{outDir}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz')
            shutil.move(registration['invtransforms'][1],f'{outDir}/slcTrans/{outname}_invDef_slc{i}.nii.gz')
        mFishLabelsIm=outReg
        ants.image_write(outReg, f'{outDir}/merfish_WarpedAllSlc.nii.gz')
