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

def RegisterfMOSTtoCCF(fMOSTFile,fMOSTtoCCFAtlasDir,outDir):
    print(fMOSTFile)

    fMOST_template_fn = f'{fMOSTtoCCFAtlasDir}/AvgfMOSTAtlas25um_v3_uint16.nii.gz'
    CCF_template_fn = f'{fMOSTtoCCFAtlasDir}/CCFTemplate25um_uint16.nii.gz'
    fMOSTtoCCFWarpDir = f'{fMOSTtoCCFAtlasDir}/fMOSTtoCCFWarp'

    movingImg = ants.image_read(fMOSTFile)
    fMOST_template = ants.image_read(fMOST_template_fn)
    
    #first register to fMOST
    registration = ants.registration(fixed=fMOST_template,
                                     moving=movingImg,
                                     type_of_transform='antsRegistrationSyNQuick[s]',
                                     verbose=True
                                     )

                                     #type_of_transform='antsRegistrationSyN[s]',
    outname = Path(Path(fMOSTFile).stem).stem
    #move warped image
    ants.image_write(registration['warpedmovout'], f'{outDir}/{outname}_WarpedTofMOST.nii.gz')
    resultTofMOST = registration['warpedmovout']    
    
    #saveTransforms
    shutil.move(registration['fwdtransforms'][0],f'{outDir}/{outname}_fwdTransformTofMOST.nii.gz')
    shutil.move(registration['fwdtransforms'][1],f'{outDir}/{outname}_affineMtxTofMOST.mat')
    shutil.move(registration['invtransforms'][1],f'{outDir}/{outname}_invTransformTofMOST.nii.gz')


    #now apply fMOST to CCF alignment
    print(f'{outDir}/{outname}_WarpedToCCF.nii.gz')
    CCF_template = ants.image_read(CCF_template_fn)

    #Tlist=[f'{fMOSTtoCCFWarpDir}/0GenericAffine.mat', f'{fMOSTtoCCFWarpDir}/1Warp.nii.gz']
    Tlist=[f'{fMOSTtoCCFWarpDir}/fMOSTtoCCFfwdTransform.nii.gz']#we now use concat'd transforms, switch to above to change back
    warped = ants.apply_transforms(fixed=CCF_template,
                                     moving=resultTofMOST,
                                     transformlist=Tlist,
                                     whichtoinvert=[False],
                                     verbose=True   
                                    )
    ants.image_write(warped, f'{outDir}/{outname}_WarpedToCCF.nii.gz')

