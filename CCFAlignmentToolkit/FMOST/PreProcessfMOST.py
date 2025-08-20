##################################################################
#
# In order to install ANTsPy, go to https://github.com/ANTsX/ANTsPy and
# we recommend building from scratch, i.e.,
#
#  $ git clone https://github.com/ANTsX/ANTsPy
#  $ cd ANTsPy
#  $ python3 setup.py install
#
# Description: This function preprocess an input image (fMOSTFile) to remove intensity
# and stripe artifacts

import ants
#from glob import glob
from pathlib import Path
import shutil
import os
import numpy as np
import SimpleITK as sitk
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

def PreProcessfMOST(fMOSTFile,outDir):
    print(fMOSTFile)

    #find largest component
    inImg = sitk.ReadImage(fMOSTFile)
    print(inImg)
    cc = sitk.ConnectedComponent(inImg >= 10);
    stats = sitk.LabelIntensityStatisticsImageFilter();    
    stats.Execute(cc,inImg)
    maxSize = 0;
    maxLabel = 0;
    for l in stats.GetLabels():
        ccSize=stats.GetPhysicalSize(l)
        if(maxSize < ccSize):
            maxSize=ccSize
            maxLabel=l

    im = sitk.GetArrayFromImage(inImg)   
    ccim = sitk.GetArrayFromImage(cc)   
    im = np.where(ccim == maxLabel, im, 0);
    im = np.where(im <= 10, 0, im);

    #use a robust Max 
    robustMax = np.percentile(im[im!=0],97);
    print(robustMax);
    im = np.where(im >= robustMax, robustMax, im);

    #find the coronal(AP) direction
    absDirMtx = np.abs(inImg.GetDirection())
    print(absDirMtx)
    #dimension with highest value in each row is the assigned dir
    lrRow = absDirMtx[[0,1,2]]
    apRow = absDirMtx[[3,4,5]]
    isRow = absDirMtx[[6,7,8]]
    print(lrRow)
    print(apRow)
    lrDirNP = 2 - lrRow.argmax(0)#in Numpy the index order is flipped
    apDirNP = 2 - apRow.argmax(0)

    #remove stripes
    savetype = im.dtype
    im = removeStripeNoise(im,lrDirNP,apDirNP)
    
        #debug code
        #plt.subplot(2,2,1)
        #plt.imshow(slc)
        #plt.subplot(2,2,2)
        #plt.imshow(np.abs(Y))
        #plt.subplot(2,2,3)
        #plt.imshow(Lo)
        #plt.subplot(2,2,4)
        #plt.imshow(im[:,:,400])
        #plt.show()
    #clean up again
    im = im.astype(np.int8)
    im = np.where(ccim == maxLabel, im, 0);
    #im = np.where(im <= 10, 0, im);


    outImg = sitk.GetImageFromArray(im)
    outImg.CopyInformation(inImg)
    outname = Path(Path(fMOSTFile).stem).stem
    outpath = f'{outDir}/{outname}_preprocessed.nii.gz'

    sitk.WriteImage(outImg, outpath)
    
    return outpath

def removeStripeNoise(im,lrDirNP,apDirNP):
    print(lrDirNP)
    print(apDirNP)


    nSize = np.shape(im);
    imOut = np.zeros(nSize)
    
    print(nSize)
    for i in range(nSize[apDirNP]):
        #if (i<400):
        #    continue
        #get coronal slice
        if apDirNP == 0:
            slc = np.squeeze(im[i,:,:])
        elif apDirNP == 1:
            slc = np.squeeze(im[:,i,:])
        elif apDirNP == 2:
            slc = np.squeeze(im[:,:,i])
        print(i)
        #print(np.shape(slc))

        #we want LR to be in the first Dim, transpose if not true
        if lrDirNP == 2:
            slc = slc.transpose()
        elif (lrDirNP == 1) and (lrDirNP < apDirNP):
            slc = slc.transpose()


        #now we filter out the stripes
        A = np.fft.fft2(slc.astype(float)); # compute FFT of the grey image
        Y = np.fft.fftshift(A); # frequency scaling
 
        slcSize=np.shape(A)
        M=slcSize[0]
        N=slcSize[1]

        # defining a typical low pass filter response H(f)
        # Low pass filter has value=1  in the 
        # low frequency region and value=0 in the high freq
        # region


        SizeFactor=6;

        Lo=np.ones(slcSize,float);
        y_center=int(np.ceil((M+1)/2));
        x_center=int(np.ceil((N+1)/2));
        w=np.floor(M/(20*SizeFactor));
        w2=np.floor(N/(25*SizeFactor));

        #create a gaussian filter
        filter2 = np.ones((int(2*w+1),int(2*w2+1)));
        gaussStopfilter = np.ones((int(2*w+1),int(2*w2+1)));

        for ii in range(int(2*w+1)):
            for j in range(int(2*w2+1)):
                d1 = (ii-(w+1))*(ii-(w+1));
                d2 = (j-(w2+1))*(j-(w2+1));
                filter2[ii,j] = np.math.exp(- (d1/(.5*w*w) + d2/(.5*w2*w2))); # d0:lower cutoff frequency
                gaussStopfilter[ii,j]= 1 - filter2[ii,j];

        signal = np.abs(Y[y_center,:]) 
        peaks, _ = find_peaks(signal,prominence=1,distance=N/(10*SizeFactor))
        #peaks, _ = find_peaks(signal,prominence=1)

        #if (i==400):
            #plt.imshow(slc)
            #print(signal[peaks])
            #print(np.argmax(signal[peaks]))
            #plt.plot(peaks,signal[peaks], "xr"); plt.plot(signal);
            #plt.show()

          #  [pks,locs]=findpeaks(abs(Y(y_center,:)),'MinPeakDistance',N/(20*SizeFactor),'SortStr','descend');
        maxPeak = np.argmax(signal[peaks])
        for x in peaks:
            #x=locs(j);
            if x == peaks[maxPeak]: #skip max peak
                 continue

            if(int(x-w2)>=0 and int(x+w2+1)<N):
                 #print(int(y_center-w))
                 #print(int(y_center+w))
                 #print(int(x-w2))
                 #print(int(x+w2))
                 Lo[int(y_center-w):int(y_center+w+1):1,int(x-w2):int(x+w2+1):1]=gaussStopfilter;


        J=Y*Lo;
        J1=np.fft.ifftshift(J);
        outslc = np.fft.ifft2(J1);
        outslc = np.abs(outslc)
        outslc[slc==0] = 0;
        outslc[outslc<0] = 0;
    
        #debug code
        #plt.subplot(2,2,1)
        #plt.imshow(slc)
        #plt.subplot(2,2,2)
        #plt.imshow(np.abs(Y))
        #plt.subplot(2,2,3)
        #plt.imshow(Lo)
        #plt.subplot(2,2,4)
        #plt.imshow(outslc)
        
        #plt.show()
        
        #revert transpose if performed
        if lrDirNP == 2:
            outslc = outslc.transpose()
        elif (lrDirNP == 1) and (lrDirNP < apDirNP):
            outslc = outslc.transpose()

        #put in correct coronal slice
        if apDirNP == 0:
            imOut[i,:,:]=outslc
        elif apDirNP == 1:
            imOut[:,i,:]=outslc
        elif apDirNP == 2:
            imOut[:,:,i]=outslc

    return imOut
