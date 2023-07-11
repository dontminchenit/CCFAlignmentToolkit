import ants
from glob import glob
from pathlib import Path
import numpy as np
import os
import pandas as pd
import SimpleITK as sitk

verbose = False;

if True:
    #SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data/2021182335_recon_batch_1_192343/192343_3226-X6435-Y14389_reg.swc'
    SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data/2021182335_recon_batch_1_191812/191812_2605-X10437-Y11829_reg.swc'
    OrientImgFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data/examples/HUST_mm_RSA/orientation_template_mm_RSA.nii.gz'
    outDir = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/HUST_Transformed'
    
    #SWCFile = '/Users/min/Dropbox (Personal)/Shared/191807_4114-X3589-Y10280.swc' 
    #SWCFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data/HUST_REGISTRATION_AllCells_OriginalSent/182724_1994-X7390-Y11953.swc'
    #OrientImgFile ='/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data/202112201620_orientation_templates/182724_mm_SLA.nii.gz'
    fMOSTImgFile = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/20211219_fmost_data/202112201148_downsampled_volumes/191812_red_mm_SLA.nii.gz'
    #outDir = '/Users/min/Documents/ResearchResults/AllenInstitute/fMost/fMOSTRegistrationModule/FullTest/Downsample_Transformed'


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
    imfMOST = sitk.ReadImage(fMOSTImgFile)

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
        pixelPt = imfMOST.TransformPhysicalPointToContinuousIndex(imOrient.TransformContinuousIndexToPhysicalPoint((swcX[k],swcY[k],swcZ[k])))
        #x[k]=pixelPt[0]
        #y[k]=pixelPt[1]
        #z[k]=pixelPt[2] 
        x[k]=worldPt[0]
        y[k]=worldPt[1]
        z[k]=worldPt[2] 
        t[k]=1 #t is always one for 3D transforms

    #create a dataframe with points from swc
    pts = pd.DataFrame({'x': x, 'y': y, 'z': z, 't': t})
    if verbose: 
        print(pts)


    #Save in world(mm) Coordinate
    outputDF = pts.copy(deep=True)
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
    #save outfile
    #outputDF.to_csv(f'{outDir}/{SWCBasename}_toPixel.swc',sep=' ',header=False, index=False)
    outputDF.to_csv(f'{outDir}/{SWCBasename}_toCCF.swc',sep=' ',header=False, index=False)
