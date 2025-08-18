# CCFAlignmentToolkit

This repository contains scripts compatible with the [ANTsX Ecosystem](https://github.com/ANTsX) for registering MERFISH and fMOST images into the Allen Common Coordinate Framework (v3). The pipelines below were developed in support of work done as part of the following publications and conferences:

- Yao, Z., Van Velthoven, C.T., Kunst, M., Zhang, M., McMillen, D., Lee, C., Jung, W., Goldy, J., Abdelhak, A., Aitken, M., Baker, K., et al. 2023. A high-resolution transcriptomic and spatial atlas of cell types in the whole mouse brain. Nature, 624(7991), pp.317-332. [https://doi.org/10.1038/s41586-023-06812-z](https://doi.org/10.1038/s41586-023-06812-z)
- Tustison, N.J., Chen, M., Kronman, F.N., Duda, J.T., Gamlin, C., Tustison, M.G., Kunst, M., Dalley, R., Sorenson, S., Wang, Q. Ng, L., et al. 2025. Modular strategies for spatial mapping of diverse cell type data of the mouse brain. Under Review.
- [Get Your Brain Straight - Hackathon 1: March 2022](HCK01_2022_Virtual/README.md)



# fMOST scripts

<p align="middle">
  <img src="https://github.com/ntustison/DevCCF-Velocity-Flow/blob/main/Manuscript/Figures/fmostPipeline.png" width="500" />
</p>
##Description

## One-time Functions 
(these are functions that only need to be run once. We will run these and will provide the end results as resources) 
### Construction of fMOST atlas 
  - Function call: antsMultivariateTemplateConstruction2.sh
  - Inputs: Collection of fMOST images to be used in atlas.
  - Outputs: fMOST average atlas

### Sequential Registration of fMOST atlas to CCF
- Function call: AtlasToCCFSequentialRegistration.py
- Inputs: Atlas & labels for fMOST atlas and CCF
- Outputs: Transform between fMOST atlas -> CCF

## Runtime Functions 
(These are functions the users will run given new images)

### Registration of new fMOST image to fMOST atlas
- Function: fMOSTRegisterToCCF.py
- Inputs: New fMOST image (downsampled) and fMOST average atlas
- Output: Transform between new fMOST image and fMOST atlas

### Applying transforms to image
- Function: ApplyTransfromTofMOST.py
- Inputs: fMOST image; transform between fMOST image->fMOST atlas; transform between fMOST atlas -> CCF
- Outputs: new fMOST image in CCF space

### Applying transforms to neurons
- Function: ApplyTransfromToSWC.py
- Inputs: SWC in new fMOST image space; transform between fMOST image->fMOST atlas; transform between fMOST atlas->CCF
- Outputs:  neurons (swc) in CCF space

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

