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

ventmfish='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_mouse2/iter0/merfish_WarpedAllSlcVent.nii.gz'
ventCCF='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_mouse2/iter0/mouse2_CCFGlobWarpedNN_ventricle_cuts.nii.gz'
ventCCF2='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_mouse2/iter0/mouse2_CCFGlobWarpedNN.nii.gz'

affCCFFull='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_mouse2/iter0/mouse2_CCFFullGlobWarpedNN.nii.gz'
affCCFSimp='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_mouse2/iter0/mouse2_CCFGlobWarpedNN.nii.gz'
affCCFAtlas='/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegPrelimDefNNvent_mouse2/iter0/mouse2_CCFAtlasGlobWarped.nii.gz'

#affCCFFullim=ants.image_read(affCCFFull)
#affCCFSimp=ants.image_read(affCCFSimp)
#affCCFAtlas=ants.image_read(affCCFAtlas)

ventmfishim=ants.image_read(ventmfish)

for i in range(57):
    #check if slc is empty
    slcsum=np.sum(ventmfishim.view()[:,:,i])
    if slcsum == 0:
        ventmfishim.view()[:,:,i] = ventmfishim.view()[:,:,i-1]

ventCCFim=ants.image_read(ventCCF)
ventCCFim2=ants.image_read(ventCCF2)
ventCCFim.view()[:,:,:]= ((ventCCFim.view()[:,:,:] + (ventCCFim2.view()[:,:,:] == 15).astype(int)) > 0).astype(int)

mFishLabelsImOrig = ants.image_read(mFishLabels)
mFishLabelsIm = ants.image_read(mFishLabels)
CCFLabelsIm = ants.image_read(CCFLabels)
CCFFullLabelsIm = ants.image_read(CCFFullLabels)
CCFAtlasIm = ants.image_read(CCFAtlas)
outDirBase=f'/Users/min/Documents/ResearchResults/AllenInstitute/merFish/RegventTest_{outname}/'
os.makedirs(outDirBase,exist_ok=True)
    

for iter in range(1):
        outDir=f'{outDirBase}/testiter{iter}/'
        os.makedirs(outDir,exist_ok=True)
        ants.image_write(ventCCFim, f'{outDir}/{outname}_CCFinput.nii.gz')
        ants.image_write(ventmfishim, f'{outDir}/{outname}_mfishinput.nii.gz')
        registration = ants.registration(fixed=ventmfishim, 
                                             moving=ventCCFim,
                                             type_of_transform='SyNOnly',
                                             syn_metric='meansquares',
                                             reg_iterations=(200, 100, 70, 40, 20),
                                             verbose=True
                                             )

        Tlist=registration['fwdtransforms']

        #move warped image
        warped = ants.apply_transforms(moving=ventCCFim,
                                             fixed=ventmfishim,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True
                                            )   
        ants.image_write(warped, f'{outDir}/{outname}_CCFVentGlobWarpedNN.nii.gz')         

        affCCFFullim=ants.image_read(affCCFFull)
        warped = ants.apply_transforms(moving=affCCFFullim,
                                             fixed=ventmfishim,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True
                                            )   
        ants.image_write(warped, f'{outDir}/{outname}_CCFFullGlobWarpedNN.nii.gz')         
        
        affCCFSimp=ants.image_read(affCCFSimp)
        warped = ants.apply_transforms(moving=affCCFSimp,
                                             fixed=ventmfishim,
                                             transformlist=Tlist,
                                             interpolator='nearestNeighbor',
                                             whichtoinvert=[False],
                                             verbose=True
                                            )   
        ants.image_write(warped, f'{outDir}/{outname}_CCFSimpGlobWarpedNN.nii.gz')         
        
        affCCFAtlas=ants.image_read(affCCFAtlas)
        warped = ants.apply_transforms(moving=affCCFAtlas,
                                             fixed=ventmfishim,
                                             transformlist=Tlist,
                                             interpolator='linear',
                                             whichtoinvert=[False],
                                             verbose=True
                                            )   
        ants.image_write(warped, f'{outDir}/{outname}_CCFAtlasGlobWarpedNN.nii.gz')         
