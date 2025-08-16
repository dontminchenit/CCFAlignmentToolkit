# CCFAlignmentToolkit

This repository contains scripts usable with the ANTS Ecosystem () for registering MERFISH and fMOST images into the Allen Common Coordinate Frame (v3).

# fMOST scripts

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

