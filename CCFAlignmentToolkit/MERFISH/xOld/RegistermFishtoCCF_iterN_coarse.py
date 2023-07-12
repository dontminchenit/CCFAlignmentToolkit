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

mFishLabels=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2/warpedImagesNN/Mouse3LabelsDilated_AppliedWarpAllSlc.nii.gz'
CCFLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNinv_mouse3_v2/iter0/mouse3_v2_CCFGlobWarpedNN.nii.gz'
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
outDirBase=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNLandmarksIterN_coarse_SynOnly_{outname}/'

os.makedirs(outDirBase,exist_ok=True)
    
LabelsMax = [3]
LabelsMin = [3]
LabelsReplFrom = [17]
LabelsReplTo = [3]
numLabels = len(LabelsMax)
for iter in range(numLabels):
        
        outDirIter = f'{outDirBase}/iter{iter}'
        os.makedirs(outDirIter, exist_ok=True)
        
        mFishLabelsIm_sel = mFishLabelsIm.copy()
        CCFLabelsIm_sel = CCFLabelsIm.copy()

        #Select labels to use this iteration
        #mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() == LabelsReplFrom[iter]] = LabelsReplTo[iter]; 
        #mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() > LabelsMax[iter]] = 0; 
        #mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() < LabelsMin[iter]] = 0; 
        mFishLabelsIm_sel.view()[mFishLabelsIm_sel.view() > 1] = 1; 
        
        ants.image_write(mFishLabelsIm_sel, f'{outDirIter}/{outname}_selLabels_mFish.nii.gz')
        
        #CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() == LabelsReplFrom[iter]] = LabelsReplTo[iter]; 
        #CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() > LabelsMax[iter]] = 0; 
        #CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() < LabelsMin[iter]] = 0; 
        CCFLabelsIm_sel.view()[CCFLabelsIm_sel.view() > 1] = 1; 
        
        ants.image_write(CCFLabelsIm_sel, f'{outDirIter}/{outname}_selLabels_CCF.nii.gz')

        outReg = mFishLabelsIm_sel.copy()
        outDirSlc = f'{outDirIter}/slcTrans'
        os.makedirs(outDirSlc, exist_ok=True)
        
        #Register per slice
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
                                             type_of_transform='antsRegistrationSyNQuick[s]',
                                             verbose=True
                                             )
            Tlist=registration['fwdtransforms']
            
            mFishFull_slc=ants.from_numpy(mFishLabelsIm.view()[:,:,i])
            warpedslc = ants.apply_transforms(moving=mFishFull_slc,
                                             fixed=CCF_slc,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False, False],
                                             verbose=True   
                                            )

            if (slcsum != 0) & (slcsum2 != 0):
                outReg.view()[:,:,i]=warpedslc.view()
            shutil.move(registration['fwdtransforms'][1],f'{outDirIter}/slcTrans/{outname}_fwdAffineMtx_slc{i}.mat')
            shutil.move(registration['fwdtransforms'][0],f'{outDirIter}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz')
            shutil.move(registration['invtransforms'][1],f'{outDirIter}/slcTrans/{outname}_invDef_slc{i}.nii.gz')
        mFishLabelsIm=outReg
        ants.image_write(outReg, f'{outDirIter}/merfish_WarpedAllSlc.nii.gz')
