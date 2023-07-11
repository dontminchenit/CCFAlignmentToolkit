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
    

outname='mouse2'

mFishLabels=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/AllLabelsMerFish_{outname}.nii.gz'
CCFLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/AllLabelsCCF.nii.gz'
CCFFullLabels='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/annotation_10.nii.gz'
CCFAtlas='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegistrationTools/average_template_10.nii.gz'

ventmfish='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/extendedLabels_mouse2/mouse2_ventricles.nii.gz'
ventCCF='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/extendedLabels_mouse2/ccf_extended_ventricles.nii.gz'

ventmfishim=ants.image_read(ventmfish)
ventCCFim=ants.image_read(ventCCF)

mFishLabelsImOrig = ants.image_read(mFishLabels)
mFishLabelsIm = ants.image_read(mFishLabels)
CCFLabelsIm = ants.image_read(CCFLabels)
CCFFullLabelsIm = ants.image_read(CCFFullLabels)
CCFAtlasIm = ants.image_read(CCFAtlas)
outDirBase=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_{outname}/'

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
        TlistGlobCCF=Tlist;
        warpedCCF = ants.apply_transforms(moving=CCFLabelsIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warpedCCF, f'{outDir}/{outname}_CCFGlobWarpedNN.nii.gz')
        
        warpedFull = ants.apply_transforms(moving=CCFFullLabelsIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warpedFull, f'{outDir}/{outname}_CCFFullGlobWarpedNN.nii.gz')
        
        warpedAtlas = ants.apply_transforms(moving=CCFAtlasIm,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='linear',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warpedAtlas, f'{outDir}/{outname}_CCFAtlasGlobWarped.nii.gz')
        
        warpedVent = ants.apply_transforms(moving=ventCCFim,
                                             fixed=mFishLabelsIm,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True   
                                            )
        ants.image_write(warpedVent, f'{outDir}/{outname}_CCFVentGlobWarpedNN.nii.gz')
        
        #warped=ants.image_read('/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelim/AllLabelsCCF_WarpedNN.nii.gz')

        outReg = mFishLabelsImOrig.copy()
        outRegVent = ventmfishim.copy()
        os.makedirs(f'{outDir}/slcTrans', exist_ok=True)
        for i in range(57):
            mFish_slc=ants.from_numpy(mFishLabelsImOrig.view()[:,:,i])
            mFishvent_slc=ants.from_numpy(ventmfishim.view()[:,:,i])
            CCF_slc=ants.from_numpy(warpedCCF.view()[:,:,i])

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

            warpedslc_vent = ants.apply_transforms(moving=mFishvent_slc,
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
                outRegVent.view()[:,:,i]=warpedslc_vent.view()
            shutil.move(registration['fwdtransforms'][1],f'{outDir}/slcTrans/{outname}_fwdAffineMtx_slc{i}.mat')
            shutil.move(registration['fwdtransforms'][0],f'{outDir}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz')
       
        registration = ants.registration(fixed=outRegVent,
                                        moving=warpedVent,
                                        type_of_transform='antsRegistrationSyNQuick[s]', #type_of_transform='Rigid',
                                        aff_metric='meansquares',
                                        syn_metric='meansquares',
                                        verbose=True
                                        )
 
        Tlist=registration['fwdtransforms']
        CCFLabelsImVent = ants.apply_transforms(moving=warpedVent,
                                          fixed=outRegVent,
                                          transformlist=Tlist,
                                          interpolator='nearestNeighbor',
                                          whichtoinvert=[False,False],
                                          verbose=True   
                                          )
        ants.image_write(CCFLabelsImVent, f'{outDir}/{outname}_CCFVentGlobWarpedNN_Deform.nii.gz')
        CCFLabelsIm = ants.apply_transforms(moving=warpedCCF,
                                          fixed=outRegVent,
                                          transformlist=Tlist,
                                          interpolator='nearestNeighbor',
                                          whichtoinvert=[False,False],
                                          verbose=True   
                                          )
        ants.image_write(CCFLabelsIm, f'{outDir}/{outname}_CCFGlobWarpedNN_Deform.nii.gz')
        mFishLabelsIm=outReg
        ants.image_write(outReg, f'{outDir}/merfish_WarpedAllSlc.nii.gz')
        ants.image_write(outRegVent, f'{outDir}/merfish_WarpedAllSlcVent.nii.gz')
        
        warpedVentinv = ants.apply_transforms(moving=outRegVent,
                                             fixed=ventCCFim,
                                             transformlist=TlistGlobCCF,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[True],
                                             verbose=True   
                                            )
        ants.image_write(warpedVentinv, f'{outDir}/merfish_inverseWarpedAllSlcVent.nii.gz')
