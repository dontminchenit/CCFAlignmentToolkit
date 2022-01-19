import ants
from glob import glob
from pathlib import Path
import numpy as np
import os
import pandas as pd

#t=glob("/Users/min/Dropbox (Personal)/Research/Projects/CCFAlignmentToolkit/Resources/TestData/*.swc")
#fMOSTFile = '/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/1_Downsampled/mouse182724red_xy32z8.nii.gz'
#fixed_fn = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/AnnotationRegistrationLabel3/CCFTemplate25um_uint16.nii.gz"
#out_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/Warped"
#warp_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/out5"

def ApplyTransformToSWC(SWCFile, fMOSTFile, ImgTofMOSTAtlasWarpDir, fMOSTtoCCFAtlasDir, outDir):

    fMOSTtoCCFWarpDir = f'{fMOSTtoCCFAtlasDir}/fMOSTtoCCFWarp'

#for SWCFile in t:
    print(SWCFile)
    f = open(SWCFile)
    header1 = f.readline()
    header2 = f.readline()
    header3 = f.readline()

    fullHeader = header1 + header2 + header3
    SWCFile = np.genfromtxt(SWCFile)
    #print(nodes.shape)
    #downsampled (we need to add this information later)
    x=SWCFile[:,2]/(32*(25/10));#dim2
    y=SWCFile[:,3]/(32*(25/10));#dim1
    z=SWCFile[:,4]/(8*(25/10));#dim3

    #load fMOST IMAGE
    outname = Path(Path(fMOSTFile).stem).stem
    im=ants.image_read(fMOSTFile);
    ImageDim = im.numpy().shape
    
    #Force a LPI orientations (determined manually).
    #in native FMOST Image dim1-LtoR, dim2=StoI, dim3=AtoP
    #in swc coordinates dim1-StoI, dim2-LtoR, dim3=AtoP 

    #Sub 182724 flip all 3 orientations and 
    d1=ImageDim[0] - y - 1;# this is corect, second dimension of swc correspond to first dimension of image. 
    d2=ImageDim[1] - x - 1;# this is corect, first dimension of swc correspond to second dimension of image.
    d3=ImageDim[2] - z - 1;
    
    #So now in reoriented Image dim1-RtoL, dim2=ItoS, dim3=PtoA
    #Swap dim2 and dim2, (PtoA and ItoS directions)
    e1 = d1
    e2 = d3
    e3 = d2

    #now apply resolution to bring to physical space
    #and negate X and Y to move to ITK WORLD SPACE
    x=-e1*.025;
    y=-e2*.025;
    z=e3*.025;
    t=e1;#last dimension is just one since we don't have dim4
    t[:] = 1;

    #create a dataframe with points
    d = {'x': x, 'y': y, 'z': z, 't':t}
    pts = pd.DataFrame(data=d)

    #apply transform from image to avg fMOST Atlas Space
    #then apply transform from avg fMOST Atlas Space to CCF 

    TList = [f'{ImgTofMOSTAtlasWarpDir}/{outname}_affineMtxTofMOST.mat', f'{ImgTofMOSTAtlasWarpDir}/{outname}_invTransformTofMOST.nii.gz', f'{fMOSTtoCCFWarpDir}/fMOSTtoCCFfwdTransform.nii.gz']
    ptsw = ants.apply_transforms_to_points(dim=3,points=pts,transformlist=TList,whichtoinvert=[True, False, False])
    print(ptsw)
    ptsw.to_csv(f'{outDir}/swctest.csv', index=False)

    #TList = [f'{ImgTofMOSTAtlasWarpDir}/{outname}_affineMtxTofMOST.mat', f'{ImgTofMOSTAtlasWarpDir}/{outname}_invTransformTofMOST.nii.gz']
    #TList2 = [f'{fMOSTtoCCFWarpDir}/fMOSTtoCCFfwdTransform.nii.gz']
    #ptsw = ants.apply_transforms_to_points(dim=3,points=pts,transformlist=TList,whichtoinvert=[True, False])
    #ptsw2 = ants.apply_transforms_to_points(dim=3,points=ptsw,transformlist=TList2,whichtoinvert=[False])
    #print(ptsw2)
    #ptsw2.to_csv(f'{outDir}/swctest2.csv', index=False)

    

    #TList = ['/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/3_AffineAligned/mouse182724red_xy32z80GenericAffine.mat']
    #ptsw = ants.apply_transforms_to_points(dim=3,points=pts,transformlist=TList,whichtoinvert=[True])

    #TList=['/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/4_RegisteredToAtlas/Atlasmouse182724red_xy32z8Warped331InverseWarp.nii.gz', '/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/4_RegisteredToAtlas/Atlasmouse182724red_xy32z8Warped330GenericAffine.mat']
    #ptsw2 = ants.apply_transforms_to_points(dim=3,points=ptsw,transformlist=TList,whichtoinvert=[False, True])
    
    #TList=['/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/5_RegisteredToCCF/1InverseWarp.nii.gz','/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/5_RegisteredToCCF/0GenericAffine.mat'] 
    #ptsw3 = ants.apply_transforms_to_points(dim=3,points=ptsw2,transformlist=TList,whichtoinvert=[False, True])
    #print(ptsw3)
    #print(x)
    #print(y)
    #print(z)
    #print(t)
    #print(SWCFile[:,4]*10)
    #print(SWCFile[:,4])
    #outname = Path(Path(x).stem).stem
    #print(f'{out_dir}/{outname}_WarpedToCCF.nii.gz')
    #fixed = ants.image_read(fixed_fn)
    #moving = ants.image_read(x)
    #warped = ants.apply_transforms(fixed=fixed,
    #                                 moving=moving,
    #                                 transformlist=[f'{warp_dir}/0GenericAffine.mat', f'{warp_dir}/1Warp.nii.gz'],
    #                                 whichtoinvert=[False, False],
    #                                 verbose=True   
    #                                )
    #ants.image_write(warped, f'{out_dir}/{outname}_WarpedToCCF.nii.gz')

