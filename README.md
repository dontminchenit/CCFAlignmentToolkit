# CCFAlignmentToolkit

This repository contains scripts compatible with the [ANTsX Ecosystem](https://github.com/ANTsX) for registering MERFISH and fMOST images into the Allen Common Coordinate Framework (v3). The pipelines below were developed in support of work done as part of the following publications and conferences:

- Yao, Z., Van Velthoven, C.T., Kunst, M., Zhang, M., McMillen, D., Lee, C., Jung, W., Goldy, J., Abdelhak, A., Aitken, M., Baker, K., et al. 2023. A high-resolution transcriptomic and spatial atlas of cell types in the whole mouse brain. Nature, 624(7991), pp.317-332. [https://doi.org/10.1038/s41586-023-06812-z](https://doi.org/10.1038/s41586-023-06812-z)
- Tustison, N.J., Chen, M., Kronman, F.N., Duda, J.T., Gamlin, C., Tustison, M.G., Kunst, M., Dalley, R., Sorenson, S., Wang, Q. Ng, L., et al. 2025. Modular strategies for spatial mapping of diverse cell type data of the mouse brain. Under Review.
- [Get Your Brain Straight - Hackathon 1: March 2022](https://github.com/dontminchenit/GetYourBrainStraight/blob/main/HCK01_2022_Virtual/README.md)

# fMOST scripts
<p align="middle">
  <img src="https://github.com/ntustison/DevCCF-Velocity-Flow/blob/main/Manuscript/Figures/fmostPipeline.png" width="500" />
</p>

## Description
The goal of this fMOST registration pipeline is a two-step process for registering into the Allen CCF. The first step is to create an fMOST specific atlas that is then registered to the Allen CCF. Step two is to use this canonical atlas to aid in the registration of new images.

## One-time Scripts 
These are scripts that only need to be run once. The final product is a registered fMOST atlas to the Allen CCF. 
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
# MERFISH scripts

<p align="middle">
  <img src="https://github.com/ntustison/DevCCF-Velocity-Flow/blob/main/Manuscript/Figures/merfishPipeline.png" width="500" />
</p>

##Description

1.) Run: 

RegistermFishtoCCF.py

To generate the initial global transform. Should be a file ending with "*_CCFGlobAffineMtx.mat" 

2.) Use this global transform to run:

ApplyGlobalCCFTransform_adjusted.py

with lines 69-85 uncommented until you find the AP/LR indexes you like.

3.) Modify line 87 to hardcode those user selected indexes, and rerun: 

ApplyGlobalCCFTransform_adjusted.py

to generate a folder with all the input images globally transformed with this adjusted matrix.

4.) Run:

RegistermFishtoCCF_iterN_Adjusted.py

pointing to the global transform folder generated in step 3.

