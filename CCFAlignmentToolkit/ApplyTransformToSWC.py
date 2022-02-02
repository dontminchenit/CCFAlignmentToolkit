import ants
from glob import glob
from pathlib import Path
import numpy as np
import os
import pandas as pd
import SimpleITK as sitk

#t=glob("/Users/min/Dropbox (Personal)/Research/Projects/CCFAlignmentToolkit/Resources/TestData/*.swc")
#fMOSTFile = '/Volumes/My Passport/fMOST/Transfer_12_15_2021/DeformNeurons/ImageChain/1_Downsampled/mouse182724red_xy32z8.nii.gz'
#fixed_fn = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/AnnotationRegistrationLabel3/CCFTemplate25um_uint16.nii.gz"
#out_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/Warped"
#warp_dir = "/Users/min/Documents/ResearchResults/AllenInstitute/fMost/ApplyAtlasTransforms/out5"

def ApplyTransformToSWC(SWCFile, fMOSTFile, OrientImgFile, ImgTofMOSTAtlasWarpDir, fMOSTtoCCFAtlasDir, outDir, verbose=0):

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

    x2=SWCFile[:,2]#dim2
    y2=SWCFile[:,3]#dim1
    z2=SWCFile[:,4]#dim3

    imageIn = sitk.ReadImage(OrientImgFile)
    imageIn2 = sitk.ReadImage(fMOSTFile)
    print(OrientImgFile)
    print(imageIn.GetDirection())
    print(imageIn.GetSpacing())
    print(imageIn.GetSize())
    print(fMOSTFile)
    print(imageIn2.GetDirection())
    print(imageIn2.GetSpacing())
    print(imageIn2.GetSize())
    print('swc-x:' + str(x2[0]))
    print('swc-y:' + str(y2[0]))
    print('swc-z:' + str(z2[0]))
    print('Physical Coordinates (OrientImg):' + str(imageIn.TransformContinuousIndexToPhysicalPoint((x2[0],y2[0],z2[0]))))
    #print(imageIn2.TransformContinuousIndexToPhysicalPoint((x[0],y[0],z[0])))
    print('Pixel Coordinate (OrientImg):' + str(imageIn.TransformPhysicalPointToContinuousIndex(imageIn.TransformContinuousIndexToPhysicalPoint((x2[0],y2[0],z2[0])))))
    print('Pixel Coordinate (DownsampleImg):' + str(imageIn2.TransformPhysicalPointToContinuousIndex(imageIn.TransformContinuousIndexToPhysicalPoint((x2[0],y2[0],z2[0])))))

    #load fMOST IMAGE
    outname = Path(Path(fMOSTFile).stem).stem
    #im=ants.image_read(fMOSTFile);
    #im2=ants.image_read(OrientImgFile);
    #print(ants.get_orientation(im));
    #print(ants.get_orientation(im2));
    #ImageDim = im.numpy().shape
    
    #Force a LPI orientations (determined manually).
    #in native FMOST Image dim1-LtoR, dim2=StoI, dim3=AtoP
    #in swc coordinates dim1-StoI, dim2-LtoR, dim3=AtoP 

    #Sub 182724 flip all 3 orientations and 
    #d1=ImageDim[0] - y - 1;# this is corect, second dimension of swc correspond to first dimension of image. 
    #d2=ImageDim[1] - x - 1;# this is corect, first dimension of swc correspond to second dimension of image.
    #d3=ImageDim[2] - z - 1;
    
    #print(d1[0])
    #print(d2[0])
    #print(d3[0])
    #print(imageIn.TransformIndexToPhysicalPoint((255,501,43)))
    
#So now in reoriented Image dim1-RtoL, dim2=ItoS, dim3=PtoA
    #Swap dim2 and dim2, (PtoA and ItoS directions)
    #e1 = d1
    #e2 = d3
    #e3 = d2


    #now apply resolution to bring to physical space
    #and negate X and Y to move to ITK WORLD SPACE
    #x=-e1*.025;
    #y=-e2*.025;
    #z=e3*.025;
    #t=e1;#last dimension is just one since we don't have dim4
    #t[:] = 1;

    x=x2.copy()
    y=y2.copy()
    z=z2.copy()
    t=x.copy()

    length = len(x)

    print(length)
    for k in range(length):
        worldPt = imageIn.TransformContinuousIndexToPhysicalPoint((x2[k],y2[k],z2[k]))
        x[k]=worldPt[0]
        y[k]=worldPt[1]
        z[k]=worldPt[2] 
        t[k]=1
        #print(worldPt) 
        #print(x[k])
        #print(y[k])
        #print(z[k])

    #create a dataframe with points
    #d = {'x': x, 'y': y, 'z': z, 't':t}
    #pts = pd.DataFrame(data=d,index=[1])
    
    pts = pd.DataFrame({'x': x, 'y': y, 'z': z, 't': t})

    print(pts)
    #apply transform from image to avg fMOST Atlas Space
    #then apply transform from avg fMOST Atlas Space to CCF 

    TList = [f'{ImgTofMOSTAtlasWarpDir}/{outname}_affineMtxTofMOST.mat', f'{ImgTofMOSTAtlasWarpDir}/{outname}_invTransformTofMOST.nii.gz', f'{fMOSTtoCCFWarpDir}/fMOSTtoCCFfwdTransform.nii.gz']
    ptsw = ants.apply_transforms_to_points(dim=3,points=pts,transformlist=TList,whichtoinvert=[True, False, False])
    print(ptsw)
    ptsw.to_csv(f'{outDir}/swctest.csv', index=False)

    tarFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/RegOut/192343_green_mm_SLA_WarpedToCCF.nii.gz'
    #tarFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/RegOut/182724_red_mm_SLA_WarpedToCCF.nii.gz'
    imageTar = sitk.ReadImage(tarFile)
    print(ptsw['x'])
    print(ptsw.iloc[0]['x'])
    print('Pixel Coordinate (CCF):' + str(imageTar.TransformPhysicalPointToContinuousIndex((ptsw.iloc[0]['x'],ptsw.iloc[0]['y'],ptsw.iloc[0]['z']))))

    #length = ptsw['x'].count
    #pixelsw = ptsw.copy
    #print(pixelsw)
    x=x2.copy()
    y=y2.copy()
    z=z2.copy()
    t=x.copy()
    for k in range(0,len(ptsw)):
        pixelCoord = imageTar.TransformPhysicalPointToContinuousIndex((ptsw.iloc[k]['x'],ptsw.iloc[k]['y'],ptsw.iloc[k]['z']))
        #pixelsw.iloc[k]['x']=pixelCoord[0]
        #pixelsw.iloc[k]['y']=pixelCoord[1]
        #pixelsw.iloc[k]['z']=pixelCoord[2]

        x[k]=pixelCoord[0]
        y[k]=pixelCoord[1]
        z[k]=pixelCoord[2]
        t[k]=1

    pixelsw = pd.DataFrame({'x': x, 'y': y, 'z': z, 't': t})
    print(pixelsw)
    pixelsw.to_csv(f'{outDir}/swctestpixel.csv', index=False)
