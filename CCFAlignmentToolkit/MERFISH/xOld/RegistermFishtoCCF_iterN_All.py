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
from scipy import ndimage
from skimage import morphology
from skimage import measure
from pathlib import Path
import shutil
import os
import numpy as np
    
def main():
    #This is the general prefix we're attaching to this set of experiments
    #TODO: not very relevant at the moment, need to clean up naming conventions throughout scripts 
    outname='mouse3_v2'
    
    #Input Directories
    mFishInDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/Mouse3'
    CCFInDir='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/Data/Mouse3_v2_regapped/CCFOrigMatched'

    #output directory 
    outDirBase=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegIterN_HipFirstCap15_{outname}/'
    os.makedirs(outDirBase,exist_ok=True)

    #Input Images
    #merfish input files
    mFishLabelsB_Di=f'{mFishInDir}/Mouse3LabelsDilated_patched.nii.gz'
    mFishLabelsLM_Di=f'{mFishInDir}/Mouse3LabelsDilated_Landmarks_patched_v2.nii.gz'
    mFishLabelsB_unDi=f'{mFishInDir}/Mouse3LabelsOrig.nii.gz'
    mFishLabelsLM_unDi=f'{mFishInDir}/Mouse3LabelsOrig_Landmarks.nii.gz'
    mFishStack=f'{mFishInDir}/Mouse3stacked.nii.gz'
    mFishRHemi=f'{mFishInDir}/merfish_right_hemisphere_v2.nii.gz'

    mFishLabelsB_Di_Im = ants.image_read(mFishLabelsB_Di)
    mFishLabelsLM_Di_Im = ants.image_read(mFishLabelsLM_Di)
    mFishLabelsB_unDi_Im = ants.image_read(mFishLabelsB_unDi)
    mFishLabelsLM_unDi_Im = ants.image_read(mFishLabelsLM_unDi)
    mFishStack_Im = ants.image_read(mFishStack)
    mFishRHemi_Im = ants.image_read(mFishRHemi)

    #CCF input files
    CCFLabelsB=f'{CCFInDir}/mouse3_v2_CCFGlobWarpedNN.nii.gz'
    CCFLabelsLM=f'{CCFInDir}/mouse3_v2_CCFLandmarksGlobWarpedNN_v2.nii.gz'
    CCFLabelsFull=f'{CCFInDir}/mouse3_v2_CCFFullGlobWarpedNN.nii.gz'
    CCFAtlas=f'{CCFInDir}/mouse3_v2_CCFAtlasGlobWarped.nii.gz'
    CCFRHemi=f'{CCFInDir}/mouse3_v2_CCFRHemiGlobWarped.nii.gz'

    CCFLabelsB_Im = ants.image_read(CCFLabelsB)
    CCFLabelsLM_Im = ants.image_read(CCFLabelsLM)
    CCFLabelsFull_Im = ants.image_read(CCFLabelsFull)
    CCFAtlas_Im = ants.image_read(CCFAtlas)
    CCFRHemi_Im = ants.image_read(CCFRHemi)

    
    #number of slices
    Nslc=mFishLabelsB_Di_Im.view().shape[2]
    print(Nslc)

    #Control vectors - These control what labels are used at each iteration.
    LabelsLevel = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1] #0 is broad labels, 1 is landmark labels   
    LabelsReplTo = [1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1]#set to 1 if merging labels, set to -1 if using all labels in range as distinct labels
    UseDistTrans = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]

    #list of labels to use at each iteration
    iterLabels0 = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
    iterLabels1 = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
    iterLabels2 = np.array([72, 73])
    iterLabels3 = np.array([74])
    iterLabels4 = np.array([75, 76])
    iterLabels5 = np.array([113, 114])
    iterLabels6 = np.array([84])
    iterLabels7 = np.array([79])
    iterLabels8 = np.array([123, 54, 64, 121, 120, 78, 94])
    iterLabels9 = np.array([124])
    iterLabels10 = np.array([61, 115, 116, 117])
    
    iterLabelsAll = [iterLabels0,
                     iterLabels1,
                     iterLabels10,
                     iterLabels2,
                     iterLabels3,
                     iterLabels4,
                     iterLabels5,
                     iterLabels6,
                     iterLabels7,
                     iterLabels8,
                     iterLabels9]
    numIter = len(iterLabelsAll)

    #start registrations
    for iter in range(numIter):

        print(iterLabelsAll[iter])    
        #output directory for current iteration
        outDirIter = f'{outDirBase}/iter{iter}'
        os.makedirs(outDirIter, exist_ok=True)
        
        #check if we're using broad or landmark labels
        if (LabelsLevel[iter] == 0):
            mFishLabelsIm_sel = mFishLabelsB_Di_Im.copy()
            CCFLabelsIm_sel = CCFLabelsB_Im.copy()
        else:
            mFishLabelsIm_sel = mFishLabelsLM_Di_Im.copy()
            CCFLabelsIm_sel = CCFLabelsLM_Im.copy()
        
        #Select label range to use this iteration, remove rest
        keepIm = np.isin(mFishLabelsIm_sel.view(),iterLabelsAll[iter])
        mFishLabelsIm_sel.view()[~keepIm] = 0; 

        #Select if we're merging labels to a particular value(>0) or keep orig labels (-1)
        if (LabelsReplTo[iter] > 0):
            mFishLabelsIm_sel.view()[keepIm] = LabelsReplTo[iter]; 
       
        #For the first iteration we divide into hemisphere 
        #TODO:hardcoded currently, make this an flag toggle in the future. 
        if (iter == 0):
            mFishLabelsIm_sel.view()[:,:,:]=mFishLabelsIm_sel.view()*250+mFishLabelsIm_sel.view()*mFishRHemi_Im.view(); 
        
        #if using distance transform instead of label
        if (UseDistTrans[iter]==1):
            mFishLabelsIm_sel.view()[:,:,:]=distTranClean(mFishLabelsIm_sel.view(),2000,50)

        #save merfish input after label selection
        ants.image_write(mFishLabelsIm_sel, f'{outDirIter}/{outname}_selLabels_mFish.nii.gz')
      
        #Now we repeat for CCF images 
        #select labels range to use this iteration 
        keepIm = np.isin(CCFLabelsIm_sel.view(),iterLabelsAll[iter])
        CCFLabelsIm_sel.view()[~keepIm] = 0; 
        
        #Select if we're merging labels in range
        if (LabelsReplTo[iter] > 0):
            CCFLabelsIm_sel.view()[keepIm] = LabelsReplTo[iter]; 
       
        #For the first iteration we divide into hemisphere 
        if (iter == 0):
            CCFLabelsIm_sel.view()[:,:,:]=CCFLabelsIm_sel.view()*250+CCFLabelsIm_sel.view()*CCFRHemi_Im.view()*500; 

        #if using distance transform instead of label
        if (UseDistTrans[iter]==1):
            CCFLabelsIm_sel.view()[:,:,:]=distTranClean(CCFLabelsIm_sel.view(),2000,50)


        #save CCF Input after label selection
        ants.image_write(CCFLabelsIm_sel, f'{outDirIter}/{outname}_selLabels_CCF.nii.gz')

        #create slc output image and directory
        outReg = mFishLabelsIm_sel.copy()
        outDirSlc = f'{outDirIter}/slcTrans'
        os.makedirs(outDirSlc, exist_ok=True)
        
        #Register between merfish and CCF per slice
        for i in range(Nslc):
            
            #select slide from images
            mFish_slc=ants.from_numpy(mFishLabelsIm_sel.view()[:,:,i])
            CCF_slc=ants.from_numpy(CCFLabelsIm_sel.view()[:,:,i])

            #check if slc is empty, if so simulate an identity transform
            #TODO: we need some better logic for this in the future
            slcsum=np.sum(mFish_slc.view())
            slcsum2=np.sum(CCF_slc.view())
            if (slcsum == 0) or (slcsum2 == 0):
                CCF_slc[0,0] = 1;
                mFish_slc=CCF_slc

            #If first iteration, we have two transforms (affine + def), otherwise just a def
            if (iter == 0):#first iteration we use an affined + weak deformation (BROAD + hemisphere)
                invertArray = [False, False]
                #transType = 'antsRegistrationSyNQuick[s]'
                transType = 'SyN'
                itersLvl=(40, 20, 10)
                numTrans = 2
            elif (iter == 1):#this is hard coded a weak deformation for the second iteration (BROAD using all labels)
                #TODO: we need another control vector that determines deformation strength.
                invertArray = [False]
                transType = 'SyNOnly'
                itersLvl=(40, 20, 10)
                numTrans = 1
            else:#all other iterations we use a stronger deformation.
                invertArray = [False]
                transType = 'SyNOnly'
                itersLvl=(70, 40, 20)
                numTrans = 1
            
            #run registration    
            if (iter == 0):#first iteration we run both affine and deformable
                registration = ants.registration(fixed=CCF_slc,
                                                moving=mFish_slc, 
                                                type_of_transform=transType,
                                                grad_step=0.1,
                                                flow_sigma=3,
                                                total_sigma=0,
                                                reg_iterations=itersLvl,
                                                aff_metric='meansquares',
                                                syn_metric='meansquares',
                                                verbose=True
                                                )
            else:#for later iterations, we only have deformable by forcing affine matrix to be identity
                registration = ants.registration(fixed=CCF_slc,
                                                moving=mFish_slc, 
                                                initial_transform='Identity',
                                                type_of_transform=transType,
                                                grad_step=0.1,
                                                flow_sigma=3,
                                                total_sigma=0,
                                                reg_iterations=itersLvl,
                                                aff_metric='meansquares',
                                                syn_metric='meansquares',
                                                verbose=True
                                                )
            #get transformation list
            if numTrans == 2:#grab both affine and deformable
                Tlist=registration['fwdtransforms']
            else:#otherwise only grab the deformable field
                Tlist=registration['fwdtransforms'][0]

            #apply transformation to current slice
            warpedslc = ants.apply_transforms(moving=mFish_slc,
                                             fixed=CCF_slc,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=invertArray,
                                             verbose=True   
                                            )

            #leave things alone if either CCF or merfish slice is empty
            if (slcsum != 0) & (slcsum2 != 0):
                outReg.view()[:,:,i]=warpedslc.view()

            #save out transformations
            shutil.move(registration['fwdtransforms'][1],f'{outDirIter}/slcTrans/{outname}_fwdAffineMtx_slc{i}.mat')
            shutil.move(registration['fwdtransforms'][0],f'{outDirIter}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz')
            shutil.move(registration['invtransforms'][1],f'{outDirIter}/slcTrans/{outname}_invDef_slc{i}.nii.gz')
        
        #save out registration result
        mFishLabelsIm=outReg
        ants.image_write(outReg, f'{outDirIter}/merfish_selLabels_WarpedAllSlc.nii.gz')

        #Apply Transformations to all merfish inputs and reassign as inputs for next iterations
        mFishLabelsB_Di_Im = applySlcTransforms(mFishLabelsB_Di_Im,CCFLabelsB_Im,0,numTrans,outDirIter,outname,'Mouse3Labels_Broad_Dilated')
        mFishLabelsLM_Di_Im = applySlcTransforms(mFishLabelsLM_Di_Im,CCFLabelsB_Im,0,numTrans,outDirIter,outname,'Mouse3Labels_Landmarks_Dilated')
        mFishLabelsB_unDi_Im = applySlcTransforms(mFishLabelsB_unDi_Im,CCFLabelsB_Im,0,numTrans,outDirIter,outname,'Mouse3Labels_Broad_unDilated')
        mFishLabelsLM_unDi_Im = applySlcTransforms(mFishLabelsLM_unDi_Im,CCFLabelsB_Im,0,numTrans,outDirIter,outname,'Mouse3Labels_Landmarks_unDilated')
        mFishStack_Im = applySlcTransforms(mFishStack_Im,CCFLabelsB_Im,1,numTrans,outDirIter,outname,'Mouse3Stack')
        mFishRHemi_Im = applySlcTransforms(mFishRHemi_Im,CCFLabelsB_Im,1,numTrans,outDirIter,outname,'Mouse3RHemi')


#subfunction for creating a clean distance transform of a binary images
def distTranClean(imIn, minCompSize, minNoiseSize):

    imOut = imIn
    Nslc = imIn.shape[2]

    #Operate per slice
    for i in range(Nslc):
        print(i)
        #extract slice
        currslc=imOut[:,:,i]

        #close image to make large connected components
        currslc_mask=ndimage.binary_closing(currslc,structure=np.ones((60,60)))

        #filter by largest CompSize size
        currslc_mask=morphology.remove_small_objects(measure.label(currslc_mask),minCompSize,connectivity=2)

        #mask with original image
        currslc = (currslc > 0) & (currslc_mask > 0)

        #filter by noise size
        currslc=morphology.remove_small_objects(measure.label(currslc),minNoiseSize,connectivity=2)
        slcsum=np.sum(currslc)

        #if slice is not empty find distance transform, otherwise just save empty img
        if(slcsum > 0):
            #calculate distance transform
            currslc=ndimage.distance_transform_edt(np.invert(currslc > 0))

            #invert and clip        
            currslc=(15-currslc)
            currslc[currslc<0]=0

        # save slice
        imOut[:,:,i]=currslc
    return imOut


#subfunction for transforming an image per section
def applySlcTransforms(movingImg,fixedImg,NN0Lin1,numTrans,workingDir,outname,saveName):
        Nslc=movingImg.view().shape[2]
        outReg = movingImg.copy()
       
        #Check if we're using linear or nearestneighbor transformations 
        if (NN0Lin1 == 0):
            interpType='nearestNeighbor' 
        else:
            interpType='linear'

        #apply transforms to each section
        for i in range(Nslc):
            input_slc=ants.from_numpy(movingImg.view()[:,:,i])
            CCF_slc=ants.from_numpy(fixedImg.view()[:,:,i])

            #Apply transforms
            if (numTrans == 1):
                invertArray = [False]
                Tlist=[f'{workingDir}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz']
            else:
                invertArray = [False, False]
                Tlist=[f'{workingDir}/slcTrans/{outname}_fwdDef_slc{i}.nii.gz', f'{workingDir}/slcTrans/{outname}_fwdAffineMtx_slc{i}.mat']
            
            warped = ants.apply_transforms(moving=input_slc,
                                             fixed=CCF_slc,
                                             transformlist=Tlist,
                                             interpolator=interpType,
                                             whichtoinvert=invertArray,
                                             verbose=True
                                             )
            outReg.view()[:,:,i]=warped.view()

        #save and return transformed image
        ants.image_write(outReg, f'{workingDir}/{saveName}_AppliedWarpAllSlc.nii.gz')
        return outReg

main()
