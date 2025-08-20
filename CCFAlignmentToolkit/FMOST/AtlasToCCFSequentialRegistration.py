##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#
#
# Description: This script is for a one time registration of the Average fMOST into the Allen CCF
# Inputs: Atlas & labels for fMOST atlas and CCF. Edit the following variables:
#    fMOSTtoCCFAtlasDir - Base Directory
#    fMOST_template_fn - fMOST Atlas constructed above
#    CCF_template_fn - Allen CCF atlas
#    fMOST_Labels_fn - Annotomical labels/landmarks for fMOST atlas
#    CCF_Labels_fn - Annotomical labels/landmarks for ALLEN CCF atlas
#
# Outputs: Transformation field and transformed atlas between fMOST atlas and Allen CCF:
#    ../fMOSTtoCCFWarp/fMOSTtoCCFfwdTransform.nii.gz
#    ../fMOSTtoCCFWarp/fMOSTLabelsWarpedtoCCF_final.nii.gz


import ants
#from glob import glob
from pathlib import Path
import shutil
import os
import sys
import numpy as np





if True:
    #load atlases
    fMOSTtoCCFAtlasDir = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/AtlasV6'
    fMOST_template_fn = f'{fMOSTtoCCFAtlasDir}/AvgfMOSTAtlas25um_v3_uint16.nii.gz'
    CCF_template_fn = f'{fMOSTtoCCFAtlasDir}/CCFTemplate25um_uint16.nii.gz'
    
    CCF_template = ants.image_read(CCF_template_fn)
    fMOST_template = ants.image_read(fMOST_template_fn)
    
    #fMOSTtoCCFWarpDir = f'{fMOSTtoCCFAtlasDir}/fMOSTtoCCFWarp'
    outDir = f'{fMOSTtoCCFAtlasDir}/fMOSTtoCCFWarp'
    os.makedirs(outDir, exist_ok=True)

    #load labels
    CCF_Labels_fn = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/AtlasV6/landmarks_v06/ccf_annotation/ccf_simplified_landmarks_filled_25_mm_LPI.nii.gz'
    fMOST_Labels_fn = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/AtlasV6/landmarks_v06/fmost_annotation/fmost_landmarks_double_sided_filled_25_mm_LPI.nii.gz'
    CCF_Labels = ants.image_read(CCF_Labels_fn)
    fMOST_Labels = ants.image_read(fMOST_Labels_fn)
    fMOST_Labels_PrevStep = fMOST_Labels #We start with the fMOST labels, this gets updated each step
   
    #Allocate Memory for labels to use at each step 
    CCF_Labels_sel = CCF_Labels.copy() 
    fMOST_Labels_sel = fMOST_Labels.copy()
   
    #this is the order we want to sequentially register the labels 
    regOrder = [2, 13, 14, 6, 9 ,12, 11, 8];
    numLabels = len(regOrder);
    
    #register each label in order
    for i in range(numLabels):
        #separate out current label to use
        currVal = regOrder[i]
        currName = str(i)
        outname = f'Step{currName}'
        print(outname)
        CCF_Labels_sel.view()[:,:,:] = (CCF_Labels.view() == currVal).astype(int)
        fMOST_Labels_sel.view()[:,:,:] = (fMOST_Labels_PrevStep.view() == currVal).astype(int)

        #save out input images for current step
        ants.image_write(CCF_Labels_sel, f'{outDir}/{outname}_CCF.nii.gz')
        ants.image_write(fMOST_Labels_sel, f'{outDir}/{outname}_fMOST.nii.gz')

        #different registrations depending on current step
        if i == 0: #full Affine+Syn for first step
            transType = 'SyN'
            iters=(100, 70, 40, 20)
            invertTrans = [False, False]
        else: #just SyN refinement for later steps
            transType = 'SyNOnly'
            iters=(70, 40, 20)
            invertTrans = [False]
       
        #register labels
        registration = ants.registration(fixed=CCF_Labels_sel,
                                     moving=fMOST_Labels_sel,
                                     type_of_transform=transType,
                                     grad_step=0.1,
                                     flow_sigma=3,
                                     total_sigma=0,
                                     reg_iterations=iters,
                                     aff_metric='meansquares',
                                     syn_metric='meansquares',
                                     verbose=True
                                     )

        #move warped image
        ants.image_write(registration['warpedmovout'], f'{outDir}/{outname}_Warped.nii.gz')
        resultTofMOST = registration['warpedmovout']    

        print(registration['fwdtransforms'])    

        #now apply to warped fMOST labels from previous step
        fMOST_Labels_Warped = ants.apply_transforms(fixed=CCF_Labels,
                                     moving=fMOST_Labels_PrevStep,
                                     transformlist=registration['fwdtransforms'],
                                     whichtoinvert=invertTrans,
                                     interpolator='nearestNeighbor',
                                     verbose=True   
                                    )
        ants.image_write(fMOST_Labels_Warped, f'{outDir}/{outname}_WarpedAllLabels.nii.gz')

        #Each step we update the moving image to the latest warped fMOST labels 
        fMOST_Labels_PrevStep = fMOST_Labels_Warped 

        #saveTransforms
        shutil.move(registration['fwdtransforms'][0],f'{outDir}/{outname}_fwdTransform.nii.gz')
        if i == 0: #save affine as well if during first step
            shutil.move(registration['fwdtransforms'][1],f'{outDir}/{outname}_fwdAffineMtx.mat')
            shutil.move(registration['invtransforms'][1],f'{outDir}/{outname}_invTransform.nii.gz')

            #we keep a list of all the fwd and inv transforms to concat later
            AllTransformsFwd = [f'{outDir}/{outname}_fwdTransform.nii.gz',f'{outDir}/{outname}_fwdAffineMtx.mat']
            AllTransformsInv = [f'{outDir}/{outname}_fwdAffineMtx.mat',f'{outDir}/{outname}_invTransform.nii.gz'] #remember to invert the affine matrix when using this
    
        else: #we don't have an affine transform after the first Step
            shutil.move(registration['invtransforms'][0],f'{outDir}/{outname}_invTransform.nii.gz')
        
            AllTransformsFwd.insert(0,f'{outDir}/{outname}_fwdTransform.nii.gz')
            AllTransformsInv.insert(i+1,f'{outDir}/{outname}_invTransform.nii.gz')

    #Loop ends here

    #Here we concatenate all the fwd transforms
    invertList = [False]*(numLabels+1) #forwards transforms doesn't require anything to be inverted

    ConcatFwdTrans = ants.apply_transforms(fixed=CCF_Labels,
                                     moving=fMOST_Labels,
                                     transformlist=AllTransformsFwd,
                                     whichtoinvert=invertList,
                                     compose=True,
                                     verbose=True
                                    )

    #Use concatenated fwd transforms on fMOST_Labels
    fMOSTLabelsToCCF_final = ants.apply_transforms(fixed=CCF_Labels,
                                     moving=fMOST_Labels,
                                     transformlist=ConcatFwdTrans,
                                     whichtoinvert=[False],
                                     interpolator='nearestNeighbor',
                                     verbose=True
                                    )
    #save out the concatenated deformation and transformed image
    shutil.move(ConcatFwdTrans, f'{outDir}/fMOSTtoCCFfwdTransform.nii.gz')
    ants.image_write(fMOSTLabelsToCCF_final, f'{outDir}/fMOSTLabelsWarpedtoCCF_final.nii.gz')


    #Next we concatenate all the inv transforms 
    invertList[0] = True  #for Inv transforms the affine matrix needs to be inverted to be inverted

    ConcatInvTrans = ants.apply_transforms(fixed=fMOST_Labels,
                                     moving=CCF_Labels,
                                     transformlist=AllTransformsInv,
                                     whichtoinvert=invertList,
                                     compose=True,
                                     verbose=True
                                    )
    
    #Use concatenated inv transforms on CCF_Labels
    CCFLabelsTofMOST_final = ants.apply_transforms(fixed=fMOST_Labels,
                                     moving=CCF_Labels,
                                     transformlist=ConcatInvTrans,
                                     whichtoinvert=[False],
                                     interpolator='nearestNeighbor',
                                     verbose=True
                                    )
    #save out the concatenated deformation and transformed image
    shutil.move(ConcatInvTrans, f'{outDir}/fMOSTtoCCFinvTransform.nii.gz')
    ants.image_write(CCFLabelsTofMOST_final, f'{outDir}/CCFLabelsWarpedtofMOST_final.nii.gz')

