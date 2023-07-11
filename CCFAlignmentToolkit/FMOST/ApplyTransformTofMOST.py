import ants
from glob import glob
from pathlib import Path
import os

def ApplyTransformTofMOST(fMOSTFile, ImgTofMOSTAtlasWarpDir, fMOSTtoCCFAtlasDir, outDir):

    #load CCF (final space) and transform between fMOST atlas and CCF
    fMOST_template_fn = f'{fMOSTtoCCFAtlasDir}/AvgfMOSTAtlas25um_v3_uint16.nii.gz'
    CCF_template_fn = f'{fMOSTtoCCFAtlasDir}/CCFTemplate25um_uint16.nii.gz'
    fMOSTtoCCFWarpDir = f'{fMOSTtoCCFAtlasDir}/fMOSTtoCCFWarp'

    print(fMOSTFile)
    outname = Path(Path(fMOSTFile).stem).stem
    print(f'{outDir}/{outname}_WarpedToCCF.nii.gz')
    
    fMOST_template = ants.image_read(fMOST_template_fn)
    moving = ants.image_read(fMOSTFile)
    
    #warp to fMOST atlas space
    warpedTofMOST = ants.apply_transforms(fixed=fMOST_template,
                                     moving=moving,
                                     transformlist=[f'{ImgTofMOSTAtlasWarpDir}/{outname}_fwdTransformTofMOST.nii.gz', f'{ImgTofMOSTAtlasWarpDir}/{outname}_affineMtxTofMOST.mat'],
                                     whichtoinvert=[False, False],
                                     verbose=True   
                                    )

    ants.image_write(warpedTofMOST, f'{outDir}/{outname}_WarpedTofMOST.nii.gz')
    
    CCF_template = ants.image_read(CCF_template_fn)
    #warp to CCF space
    #Tlist=[f'{fMOSTtoCCFWarpDir}/0GenericAffine.mat', f'{fMOSTtoCCFWarpDir}/1Warp.nii.gz']
    Tlist=[f'{fMOSTtoCCFWarpDir}/fMOSTtoCCFfwdTransform.nii.gz']#we now use concat'd transforms, switch to above to change back
    warpedToCCF = ants.apply_transforms(fixed=CCF_template,
                                     moving=warpedTofMOST,
                                     transformlist=Tlist,
                                     whichtoinvert=[False],
                                     verbose=True   
                                    )

    ants.image_write(warpedToCCF, f'{outDir}/{outname}_WarpedToCCF.nii.gz')
