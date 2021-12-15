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
#help(ants.write_transform)
#help(ants.registration)
from glob import glob
from pathlib import Path
import os

in_dir= "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/Inputs"
out_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/Outputs"
atlas_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/Atlas"
t=glob(f'{in_dir}/*.nii.gz')

fMOST_template_fn = f'{atlas_dir}/AvgfMOSTAtlas25um_v3_uint16.nii.gz'
CCF_template_fn = f'{atlas_dir}/CCFTemplate25um_uint16.nii.gz'
fMOSTtoCCFwarp_dir = f'{atlas_dir}/fMOSTtoCCFWarp/'

for x in t:
    print(x)

    movingImg = ants.image_read(x)
    fMOST_template = ants.image_read(fMOST_template_fn)
    #first register to fMOST
    registration = ants.registration(fixed=fMOST_template,
                                     moving=movingImg,
                                     type_of_transform='antsRegistrationSyN[s]',
                                     verbose=True
                                     )
#                                     type_of_transform='SyN',
#                                     syn_metric='CC',
#                                     reg_iterations=(100,70,50,20),
#                                     verbose=True
#                                     )

    outname = Path(Path(x).stem).stem
    ants.image_write(registration['warpedmovout'], f'{out_dir}/{outname}_WarpedTofMOST.nii.gz')
    resultTofMOST = registration['warpedmovout']    

    #now apply fMOST to CCF alignment
    print(f'{out_dir}/{outname}_WarpedToCCF.nii.gz')
    CCF_template = ants.image_read(CCF_template_fn)
    warped = ants.apply_transforms(fixed=CCF_template,
                                     moving=resultTofMOST,
                                     transformlist=[f'{fMOSTtoCCFwarp_dir}/0GenericAffine.mat', f'{fMOSTtoCCFwarp_dir}/1Warp.nii.gz'],
                                     whichtoinvert=[False, False],
                                     verbose=True   
                                    )
    ants.image_write(warped, f'{out_dir}/{outname}_WarpedToCCF.nii.gz')

