import ants
from glob import glob
from pathlib import Path
import os

#t=glob("/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/*.nii.gz")

fixed_fn = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/AnnotationRegistrationLabel3/CCFTemplate25um_uint16.nii.gz"
out_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/Warped"
warp_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/out5"
def ApplyTransformTofMOST():
    print(x)
    outname = Path(Path(x).stem).stem
    print(f'{out_dir}/{outname}_WarpedToCCF.nii.gz')
    fixed = ants.image_read(fixed_fn)
    moving = ants.image_read(x)
    warped = ants.apply_transforms(fixed=fixed,
                                     moving=moving,
                                     transformlist=[f'{warp_dir}/0GenericAffine.mat', f'{warp_dir}/1Warp.nii.gz'],
                                     whichtoinvert=[False, False],
                                     verbose=True   
                                    )
    ants.image_write(warped, f'{out_dir}/{outname}_WarpedToCCF.nii.gz')
