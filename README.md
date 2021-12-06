# CCFAlignmentToolkit
One-time (these are functions that only need to be run once. We will run these and will provide the end results as resources) 
1) Construction of fMOST atlas 
Inputs: Collection of fMOST images to be used in atlas.
Outputs: fMOST average atlas

2) Sequential Registration of fMOST atlas to CCF
Inputs: Atlas & labels for fMOST atlas and CCF
Outputs: Transform between fMOST atlas -> CCF

User Run (These are functions the users will run given new images)
3) Registration of new fMOST image to fMOST atlas
Inputs: New fMOST image (downsampled) and fMOST average atlas
Output: Transform between new fMOST image and fMOST atlas

4)Applying transforms to image
Inputs: fMOST image; transform between fMOST image->fMOST atlas; transform between fMOST atlas -> CCF
Outputs: new fMOST image in CCF space

5)Applying transforms to neurons
Inputs: SWC in new fMOST image space; transform between fMOST image->fMOST atlas; transform between fMOST atlas->CCF
Outputs:  neurons (swc) in CCF space