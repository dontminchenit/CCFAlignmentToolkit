import ants
from glob import glob
from pathlib import Path
import numpy as np
import os
import pandas as pd
import SimpleITK as sitk

def ApplyTransformToSWC(SWCFile, fMOSTFile, OrientImgFile, ImgTofMOSTAtlasWarpDir, fMOSTtoCCFAtlasDir, outDir, verbose=False, targetCCF0fMOST1=0):

    fMOSTtoCCFWarpDir = f'{fMOSTtoCCFAtlasDir}/fMOSTtoCCFWarp'

    SWCBasename = Path(SWCFile).stem
    print('Transforming SWC file:' + SWCBasename)
    #Read in the header for SWC file, if we want to use
    f = open(SWCFile)
    header1 = f.readline()
    header2 = f.readline()
    header3 = f.readline()

    fullHeader = header1 + header2 + header3
    
    #Read in SWC file
    SWCData = np.genfromtxt(SWCFile)
    swcID=SWCData[:,0].astype(int)#swc x coord
    swcType=SWCData[:,1].astype(int)#swc x coord
    swcX=SWCData[:,2]#swc x coord
    swcY=SWCData[:,3]#swc y coord
    swcZ=SWCData[:,4]#swc z coord
    swcRadius=SWCData[:,5]#swc x coord
    swcParent=SWCData[:,6].astype(int)#swc x coord

    #load fMOST and Orientation images
    imOrient = sitk.ReadImage(OrientImgFile)
    imfMOST = sitk.ReadImage(fMOSTFile)
    fMOSTBasename = Path(Path(fMOSTFile).stem).stem
   
    if verbose: 
        print(OrientImgFile)
        print(imOrient.GetDirection())
        print(imOrient.GetSpacing())
        print(imOrient.GetSize())
        print(fMOSTFile)
        print(imfMOST.GetDirection())
        print(imfMOST.GetSpacing())
        print(imfMOST.GetSize())
        print('swc-x:' + str(swcX[0]))
        print('swc-y:' + str(swcY[0]))
        print('swc-z:' + str(swcZ[0]))
        print('Physical Coordinates (OrientImg):' + str(imOrient.TransformContinuousIndexToPhysicalPoint((swcX[0],swcY[0],swcZ[0]))))
        print('Pixel Coordinate (OrientImg):' + str(imOrient.TransformPhysicalPointToContinuousIndex(imOrient.TransformContinuousIndexToPhysicalPoint((swcX[0],swcY[0],swcZ[0])))))
        print('Pixel Coordinate (DownsampleImg):' + str(imfMOST.TransformPhysicalPointToContinuousIndex(imOrient.TransformContinuousIndexToPhysicalPoint((swcX[0],swcY[0],swcZ[0])))))

    #make copy of the coord arrays, this will store world coordinates 
    x=swcX.copy()
    y=swcY.copy()
    z=swcZ.copy()
    t=x.copy()

    length = len(x)
    #use Orientation Header image to find world coordinates for swc coordinates
    for k in range(length):
        worldPt = imOrient.TransformContinuousIndexToPhysicalPoint((swcX[k],swcY[k],swcZ[k]))
        x[k]=worldPt[0]
        y[k]=worldPt[1]
        z[k]=worldPt[2] 
        t[k]=1 #t is always one for 3D transforms

    #create a dataframe with points from swc
    pts = pd.DataFrame({'x': x, 'y': y, 'z': z, 't': t})
    if verbose: 
        print(pts)

    #apply transforms: From input image space ->  avg fMOST Atlas Space ->CCF
    if targetCCF0fMOST1 == 0:
        TList = [f'{ImgTofMOSTAtlasWarpDir}/{fMOSTBasename}_affineMtxTofMOST.mat', f'{ImgTofMOSTAtlasWarpDir}/{fMOSTBasename}_invTransformTofMOST.nii.gz', f'{fMOSTtoCCFWarpDir}/fMOSTtoCCFinvTransform.nii.gz']
        warpedPts = ants.apply_transforms_to_points(dim=3,points=pts,transformlist=TList,whichtoinvert=[True, False, False])
    elif targetCCF0fMOST1 == 1:
        #Use below if only transforming to fMOST Space
        TListfMOSTOnly = [f'{ImgTofMOSTAtlasWarpDir}/{fMOSTBasename}_affineMtxTofMOST.mat', f'{ImgTofMOSTAtlasWarpDir}/{fMOSTBasename}_invTransformTofMOST.nii.gz']
        warpedPts = ants.apply_transforms_to_points(dim=3,points=pts,transformlist=TListfMOSTOnly,whichtoinvert=[True, False])
    
    if verbose: 
        print(warpedPts)


    #Save in world(mm) Coordinate
    outputDF = warpedPts.copy(deep=True)
    outputDF.drop(columns='t',axis=1,inplace=True)
    outputDF.insert(0,'ID', swcID)
    outputDF['ID'] = outputDF['ID'].astype(int)
    outputDF.insert(1,'Type', swcType)
    outputDF['Type'] = outputDF['Type'].astype(int)
    outputDF.insert(5,'Radius', swcRadius)
    outputDF.insert(6,'Parent', swcParent)
    outputDF['Parent'] = outputDF['Parent'].astype(int)
    if verbose:
        print(outputDF)

    #load CCF so we can output in pixel coordinates
    if targetCCF0fMOST1 == 0:
        Tar_template_fn = f'{fMOSTtoCCFAtlasDir}/CCFTemplate25um_uint16.nii.gz'
        templateName = 'CCF'
    elif targetCCF0fMOST1 == 1:
    #Use below if only transforming to fMOST space
        Tar_template_fn = f'{fMOSTtoCCFAtlasDir}/AvgfMOSTAtlas25um_v3_uint16.nii.gz'
        templateName = 'AvgfMOST'
    imTemplate = sitk.ReadImage(Tar_template_fn)
   
    #save in mm space
    outputDF.to_csv(f'{outDir}/{SWCBasename}_WarpTo{templateName}mm.swc',sep=' ',header=False, index=False)
    
    if verbose: 
        print('Pixel Coordinate (Template):' + str(imTemplate.TransformPhysicalPointToContinuousIndex((warpedPts.iloc[0]['x'],warpedPts.iloc[0]['y'],warpedPts.iloc[0]['z']))))
    xPix=swcX.copy()
    yPix=swcY.copy()
    zPix=swcZ.copy()
    for k in range(0,len(warpedPts)):
        pixelCoord = imTemplate.TransformPhysicalPointToContinuousIndex((warpedPts.iloc[k]['x'],warpedPts.iloc[k]['y'],warpedPts.iloc[k]['z']))

        xPix[k]=pixelCoord[0]
        yPix[k]=pixelCoord[1]
        zPix[k]=pixelCoord[2]

    outputDF.x = xPix 
    outputDF.y = yPix 
    outputDF.z = zPix 
    if verbose:
        print(outputDF)
    #save in pixel space
    outputDF.to_csv(f'{outDir}/{SWCBasename}_WarpTo{templateName}pixel.swc',sep=' ',header=False, index=False)
