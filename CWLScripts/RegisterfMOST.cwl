#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool


requirements:
  DockerRequirement:
    dockerPull: "ccfalignmenttoolkit"
    dockerOutputDirectory: /data/output
  SubworkflowFeatureRequirement: {}

baseCommand: ["python3", "/opt/src/RegisterfMOST.py"]
inputs:
  inputImage:
    type: File
    inputBinding:
      position: 1

  atlasDir:
    type: Directory
    inputBinding:
      position: 2

  useQuickAnts:
    type: int
    inputBinding:
      position: 3
    default: 1

outputs: 
  affineMtx:  
    type: File
    outputBinding:
      glob: "*.mat"
  
  fwdTransform:  
    type: File
    outputBinding:
      glob: "*fwdTransformTofMOST.nii.gz"
  
  invTransform:  
    type: File
    outputBinding:
      glob: "*invTransformTofMOST.nii.gz"
  
  imgWarpedToCCF:  
    type: File
    outputBinding:
      glob: "*WarpedToCCF.nii.gz"
