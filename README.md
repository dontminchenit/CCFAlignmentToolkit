# CCFAlignmentToolkit

This repository contains scripts compatible with the [ANTsX Ecosystem](https://github.com/ANTsX) for registering MERFISH and fMOST images into the Allen Common Coordinate Framework (v3). The pipelines below were developed in support of work done as part of the following publications and conferences:

- Yao, Z., Van Velthoven, C.T., Kunst, M., Zhang, M., McMillen, D., Lee, C., Jung, W., Goldy, J., Abdelhak, A., Aitken, M., Baker, K., et al. 2023. A high-resolution transcriptomic and spatial atlas of cell types in the whole mouse brain. Nature, 624(7991), pp.317-332. [https://doi.org/10.1038/s41586-023-06812-z](https://doi.org/10.1038/s41586-023-06812-z)
- Tustison, N.J., Chen, M., Kronman, F.N., Duda, J.T., Gamlin, C., Tustison, M.G., Kunst, M., Dalley, R., Sorenson, S., Wang, Q. Ng, L., et al. 2025. Modular strategies for spatial mapping of diverse cell type data of the mouse brain. Under Review.
- [Get Your Brain Straight - Hackathon 1: March 2022](https://github.com/dontminchenit/GetYourBrainStraight/blob/main/HCK01_2022_Virtual/README.md)

# fMOST Registration Pipeline
<p align="middle">
  <img src="https://github.com/ntustison/DevCCF-Velocity-Flow/blob/main/Manuscript/Figures/fmostPipeline.png" width="500" />
</p>

## Description
The goal of this fMOST registration pipeline is a two-step process for registering into the Allen CCF. The first step is to create an fMOST specific atlas that is then registered to the Allen CCF. This step only has to be performed once. Step two is to use this canonical atlas to atlas transform to aid in the registration of new fMOST images into the CCF, and move associated neuron reconstructions into the atlas spaces. 

## One-time Scripts 
These are scripts that only need to be run once. The final product is a registered fMOST atlas to the Allen CCF, and associated transforms. 
### Construction of fMOST atlas 
  - Script: **antsMultivariateTemplateConstruction2.sh**
  - Inputs: Collection of fMOST images to be used in constructing the atlas.
  - Output: fMOST average atlas

### Sequential Registration of fMOST atlas to CCF
- Script: **AtlasToCCFSequentialRegistration.py**
- Inputs: Atlas & labels for fMOST atlas and CCF. Edit the following variables:
  - fMOSTtoCCFAtlasDir - Base Directory
  - fMOST_template_fn - fMOST Atlas constructed above
  - CCF_template_fn - Allen CCF atlas
  - fMOST_Labels_fn - Annotomical labels/landmarks for fMOST atlas
  - CCF_Labels_fn - Annotomical labels/landmarks for ALLEN CCF atlas
  
- Outputs: Transformation field and transformed atlas between fMOST atlas and Allen CCF
  - _../fMOSTtoCCFWarp/fMOSTtoCCFfwdTransform.nii.gz_ 
  - _../fMOSTtoCCFWarp/fMOSTLabelsWarpedtoCCF_final.nii.gz_

## Runtime Script
These are functions the users will run given new fMOST images or neuron reconstructions

### Registration of new fMOST image to fMOST atlas
- Function: **RegisterfMOSTtoCCF.py**
- Inputs: New fMOST image (downsampled) and fMOST average atlas
  - fMOSTFile - fMOST file to be registered
  - fMOSTtoCCFAtlasDir - Directory containing the atlas to atlas registration results (see above)
  - outDir - Output directory
  - quickANTS - flag to use a quick run of ANTS (default = 1)
- Output: Transform between new fMOST image and fMOST atlas and the CCF. Outputs are saved to the folder {outDir} specified at input. With the prefix {outName} derived from the input fMOST image name.
  - _{outDir}/{outname}_fwdTransformTofMOST.nii.gz_ - foward deformation field to fMOST atlas
  - _{outDir}/{outname}_affineMtxTofMOST.mat_ - affine matrix to fMOST atlas
  - _{outDir}/{outname}_invTransformTofMOST.nii.gz_ - inverse deformation field to fMOST atlas
  - _{outDir}/{outname}_WarpedToCCF.nii.gz_ - Warped fMOST image in Allen CCF

### Applying transforms from registration to images 
- Function: **ApplyTransfromTofMOST.py**
- Inputs:
  - fMOSTFile - new fMOST image to apply transformations
  - ImgTofMOSTAtlasWarpDir - Directory containing the image to atlas registration results (see above)
  - fMOSTtoCCFAtlasDir - Directory containing the atlas to atlas registration results (see above)
  - outDir - Output directory
- Outputs: Outputs are saved to the folder {outDir} specified at input. With the prefix {outName} derived from the input fMOST image name.
  - _{outDir}/{outname}_WarpedToCCF.nii.gz_ - Image transformed to Allen CCF
  - _{outDir}/{outname}_WarpedTofMOST.nii.gz_ - Image transformed to the fMOST Atlas

### Applying transforms to neuron reconstructions in the same space
- Function: **ApplyTransfromToSWC.py**
- Inputs: SWC in new fMOST image space; transform between fMOST image->fMOST atlas; transform between fMOST atlas->CCF
  - SWCFile - Neuron reconstruction file (.swc)
  - fMOSTFile - new fMOST image to apply transformations
  - OrientImgFile - Orientation file
  - ImgTofMOSTAtlasWarpDir - Directory containing the image to atlas registration results (see above)
  - fMOSTtoCCFAtlasDir - Directory containing the atlas to atlas registration results (see above)
  - outDir - Output directory
  - verbose(default=False) - write out additional information
  - targetCCF0fMOST1(default = -) - move neuron reconstruction to Allen CCF (=0) or fMOST atlas (=1)
- Outputs:  Neuron reconstructions (.swc) in CCF space. Outputs are saved to the folder {outDir} specified at input. With the prefix {SWCBasename} derived from the input swc filename.
  -  _{outDir}/{SWCBasename}_WarpToCCFpixel.swc_

# MERFISH to CCF Registration 

<p align="middle">
  <img src="https://github.com/ntustison/DevCCF-Velocity-Flow/blob/main/Manuscript/Figures/merfishPipeline.png" width="500" />
</p>

## Description

The goal of this MERFISH registration pipeline is to perform a manually assisted high accuracy 2.5D registeration of a mouse brain into the Allen CCF. The resulting transform can be use to move gene expression and other data associated with the MERFISH image into the CCF. It consists of the following 3 steps, and running their associated scripts in sequence. 

## Step 1: Global registration of MERFISH brain into the CCF to match the correct global orientation of the brains.

- Script: RegistermFishtoCCF.py
- Inputs:
  - outname - name prefix attached to results
  - mFishLabels - Broad labels for tissue types in the MERFISH image
  - CCFLabels - Broad labels for tissue types in the Allen CCF
  - CCFLandmarks - Fine labels for key structures in the MERFISH image
  - CCFFullLabels  - Fine labels for key structures in the Allen CCF
  - CCFAtlas - Allen CCF atlas image
  - outDirBase - Base directory where results will be saved
- Outputs:
  - Generate the initial global transform. A file ending with "*_CCFGlobAffineMtx.mat" in the outDirBase

## Step 2: Apply this transform in reverse to the Allen CCF to match slices of the CCF to the space of each MERFISH section

- Script: ApplyGlobalCCFTransform_adjusted.py
- Inputs:
  - outname - name prefix attached to results
  - mFishLabels - Broad labels for tissue types in the MERFISH image
  - CCFLabels - Broad labels for tissue types in the Allen CCF
  - CCFLandmarks - Fine labels for key structures in the MERFISH image
  - CCFFullLabels  - Fine labels for key structures in the Allen CCF
  - CCFAtlas - Allen CCF atlas image
  - outDir - Base directory where results will be saved
  - inputDir - output directory from Step 1
- Outputs:
  - Folder with all the input images are globally transformed with this adjusted matrix.

## Step 3: Section based deforable registeration between the MERFISH images and Allen CCF

- Script: RegistermFishtoCCF_iterN_Adjusted.py
- Inputs:
  -  outname - name prefix attached to results
  -  mFishInDir - input directory with all the input MERFISH images and labels
  -  CCFInDir - output directory with globally aligned Allen CCF, from Step 2
  -  outDirBase - Base directory where results will be saved
- Outputs:
  - Folder with registered MERFISH images, and deformation fields for transforming data from the MERFISH brain to the Allen CCF

