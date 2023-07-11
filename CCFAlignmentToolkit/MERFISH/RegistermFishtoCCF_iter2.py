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
#from glob import glob
from pathlib import Path
import shutil
import os
import numpy as np
    

outname='mouse3_v2'

mFishLabels=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2/warpedImages/Mouse3LabelsDilated_Landmarks_AppliedWarpAllSlc.nii.gz'
CCFLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNinv_mouse3_v2/iter0/mouse3_v2_CCFLandmarksGlobWarpedNN.nii.gz'
#CCFLandmarks='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/reference_ccf_landmark.nii.gz'
#CCFFullLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/annotation_10.nii.gz'
#CCFAtlas='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/average_template_10.nii.gz'

mFishLabelsImOrig = ants.image_read(mFishLabels)
Nslc=mFishLabelsImOrig.view().shape[2]

print(Nslc)

mFishLabelsIm = ants.image_read(mFishLabels)
CCFLabelsIm = ants.image_read(CCFLabels)
#CCFLandmarksIm = ants.image_read(CCFLandmarks)
#CCFFullLabelsIm = ants.image_read(CCFFullLabels)
#CCFAtlasIm = ants.image_read(CCFAtlas)
outDirBase=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNLandmarks76_SynOnly_{outname}/'

os.makedirs(outDirBase,exist_ok=True)
    
LabelsToUse = [73, 74, 75, 76]
numLabels = len(LabelsToUse)
for iter in range(1):
        
        mFishLabelsIm_sel = mFishLabelsIm.copy()
        CCFLabelsIm_sel = CCFLabelsIm.copy()

        mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() > 76] = 0; 
        mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() < 75] = 0; 
        mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() == 75] = 76; 
        
        ants.image_write(mFishLabelsIm_sel, f'{outDirBase}/{outname}_selLabels_mFish.nii.gz')
        
        CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() > 76] = 0; 
        CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() < 75] = 0; 
        CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() == 75] = 76; 

        ants.image_write(CCFLabelsIm_sel, f'{outDirBase}/{outname}_selLabels_CCF.nii.gz')

        outReg = mFishLabelsIm_sel.copy()
        os.makedirs(f'{outDirBase}/slcTrans', exist_ok=True)
        
        for i in range(Nslc):
            mFish_slc=ants.from_numpy(mFishLabelsIm_sel.view()[:,:,i])
            CCF_slc=ants.from_numpy(CCFLabelsIm_sel.view()[:,:,i])

            #check if slc is empty
            slcsum=np.sum(mFish_slc.view())
            slcsum2=np.sum(CCF_slc.view())
            if (slcsum == 0) or (slcsum2 == 0):
                CCF_slc[0,0] = 1;
                mFish_slc=CCF_slc

            registration = ants.registration(fixed=CCF_slc,
                                             moving=mFish_slc, 
                                             type_of_transform='SyNOnly', #type_of_transform='Rigid',
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
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )

            if slcsum != 0:
                #outSlc=registration['warpedmovout']
                #outReg.view()[:,:,i]=outSlc.view()
                outReg.view()[:,:,i]=warpedslc.view()
            #shutil.move(registration['fwdtransforms'][1],f'{outDirBase}/slcTrans/{outname}_fwdAffineMtx_slc{i}.mat')
            shutil.move(registration['fwdtransforms'][0],f'{outDirBase}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz')
            shutil.move(registration['invtransforms'][0],f'{outDirBase}/slcTrans/{outname}_invDef_slc{i}.nii.gz')
        mFishLabelsIm=outReg
        ants.image_write(outReg, f'{outDirBase}/merfish_WarpedAllSlc.nii.gz')
